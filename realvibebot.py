import time
import telebot
from telebot import types

# ============ НАСТРОЙКИ ============
TOKEN = "8330900181:AAHCcdEUiSubo_BoHrGPfPNdpZeF5W35L_w"   # <-- вставь сюда токен RealVibeBot
SUPPORT_USERNAME = "VibeSupportbot"  # без @
# Если у тебя есть file_id анимированного стикера — вставь его в START_STICKER_ID.
# Иначе оставь None — бот отправит обычное эмодзи в приветствии.
START_STICKER_ID = None  # пример: "CAACAgUAAxkBAA..." или None
# ====================================

bot = telebot.TeleBot(TOKEN)

# очередь ожидания (список chat_id)
waiting_users = []

# активные чаты: {user_id: partner_id}
active_chats = {}

# вспомог: возвращает главное меню клавиатуры
def main_menu_markup():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row(types.KeyboardButton("🔍 Найти собеседника"))
    kb.row(types.KeyboardButton("ℹ️ О проекте"), types.KeyboardButton("📩 Поддержка"))
    return kb

# клавиатура в чате (завершить, следующий)
def chat_markup():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row(types.KeyboardButton("🚫 Завершить"), types.KeyboardButton("🔄 Следующий"))
    return kb

# ---------- /start ----------
@bot.message_handler(commands=['start'])
def handle_start(message):
    chat_id = message.chat.id

    # 1) Стикер (если задан)
    if START_STICKER_ID:
        try:
            bot.send_sticker(chat_id, START_STICKER_ID)
        except Exception:
            # если стикер не отправился — ничего плохого
            pass
    else:
        # если нет стикера — отправим крупное эмодзи (быстрее и надёжнее)
        bot.send_message(chat_id, "💜")

    # 2) Приветственный текст
    welcome = (
        "💜 RealVibeBot 💜\n\n"
        "Здравствуйте! 👋\n"
        "Здесь вы можете найти анонимного собеседника и просто приятно пообщаться.\n\n"
        "Нажмите кнопку «🔍 Найти собеседника», чтобы начать поиск."
    )
    sent = bot.send_message(chat_id, welcome, reply_markup=main_menu_markup())

    # 3) Симуляция лайка — бот отправляет под последним сообщением сердечко (reply)
    try:
        time.sleep(0.5)
        bot.send_message(chat_id, "💜", reply_to_message_id=sent.message_id)
    except Exception:
        pass

# ---------- Обработка пользовательских сообщений ----------
@bot.message_handler(func=lambda m: m.chat.id)
def handle_all_messages(message):
    chat_id = message.chat.id
    text = message.text or ""

    # Если пользователь находится в активном чате — пересылаем сообщение партнёру
    if chat_id in active_chats:
        partner = active_chats.get(chat_id)
        if partner:
            try:
                bot.send_message(partner, text)
            except Exception:
                # если не удалось отправить (например, блокировка) — уведомляем пользователя
                bot.send_message(chat_id, "⚠️ Не удалось отправить сообщение собеседнику.")
        else:
            bot.send_message(chat_id, "Ошибка чата — попробуйте завершить диалог и начать заново.")
        return

    # Если пользователь нажал "Найти собеседника"
    if text == "🔍 Найти собеседника":
        if chat_id in active_chats:
            bot.send_message(chat_id, "Вы уже в чате. Чтобы завершить — нажмите 🚫 Завершить.", reply_markup=chat_markup())
            return

        # если в очереди есть кто-то, кроме самого себя — соединяем
        if waiting_users:
            # убираем самого себя, если он случайно там есть
            waiting_users_filtered = [u for u in waiting_users if u != chat_id]
            if waiting_users_filtered:
                partner_id = waiting_users_filtered.pop(0)
                # обновим очередь: удалим partner_id
                waiting_users[:] = [u for u in waiting_users if u != partner_id]
                # создаём активный чат
                active_chats[chat_id] = partner_id
                active_chats[partner_id] = chat_id

                # сообщаем обоим
                bot.send_message(chat_id, "🎯 Собеседник найден! Можете начинать общение.", reply_markup=chat_markup())
                bot.send_message(partner_id, "🎯 Собеседник найден! Можете начинать общение.", reply_markup=chat_markup())
                return

        # иначе ставим в очередь ожидания
        if chat_id not in waiting_users:
            waiting_users.append(chat_id)
        bot.send_message(chat_id, "⏳ Ищу вам собеседника... Пожалуйста, подождите.", reply_markup=types.ReplyKeyboardRemove())
        return

    # Кнопка "О проекте"
    if text == "ℹ️ О проекте":
        about = (
            "💜 RealVibe — анонимный чат, где можно познакомиться и приятно пообщаться.\n\n"
            "Никаких фото и анкет — только живое общение.\n\n"
            "Уважайте друг друга. Если возник вопрос — нажмите «📩 Поддержка». "
        )
        # Поддержка будет доступна через ссылку
        support_url = f"https://t.me/{SUPPORT_USERNAME}"
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("📩 Перейти в поддержку", url=support_url))
        bot.send_message(chat_id, about, reply_markup=markup)
        return

    # Кнопка "Поддержка" — открываем ссылку на отдельный бот
    if text == "📩 Поддержка":
        support_url = f"https://t.me/{SUPPORT_USERNAME}"
        bot.send_message(chat_id, f"Для связи с поддержкой перейдите по ссылке:\n{support_url}", reply_markup=types.ReplyKeyboardMarkup(resize_keyboard=True).row(types.KeyboardButton("🔍 Найти собеседника")))
        return

    # Завершение чата
    if text == "🚫 Завершить" or text == "/stop":
        if chat_id in active_chats:
            partner = active_chats.pop(chat_id, None)
            if partner:
                # удаляем связь у партнёра
                active_chats.pop(partner, None)
                try:
                    bot.send_message(partner, "❌ Собеседник завершил диалог.", reply_markup=main_menu_markup())
                except Exception:
                    pass
            bot.send_message(chat_id, "❌ Диалог завершён.", reply_markup=main_menu_markup())
        else:
            bot.send_message(chat_id, "Вы не находитесь в чате.", reply_markup=main_menu_markup())
        return

    # Следующий (переход к новому собеседнику)
    if text == "🔄 Следующий":
        # если в чате — завершаем его и добавляем в очередь
        if chat_id in active_chats:
            partner = active_chats.pop(chat_id, None)
            if partner:
                active_chats.pop(partner, None)
                try:
                    bot.send_message(partner, "🔄 Собеседник перешёл к следующему чату.", reply_markup=main_menu_markup())
                except Exception:
                    pass
            bot.send_message(chat_id, "🔄 Идёт поиск нового собеседника...", reply_markup=types.ReplyKeyboardRemove())
            # снова в очередь
            if chat_id not in waiting_users:
                waiting_users.append(chat_id)
            return
        else:
            bot.send_message(chat_id, "Вы не находитесь в чате. Нажмите «🔍 Найти собеседника», чтобы начать.")
            return

    # По умолчанию — если не в чате и пользователь написал текст (не команды) — подсказка
    bot.send_message(chat_id, "Чтобы начать — нажмите «🔍 Найти собеседника».", reply_markup=main_menu_markup())

# Обработка выхода (например, если пользователь удалил бота или недоступен)
# В простом варианте мы не отслеживаем disconnect отдельно; если отправка сообщения партнёру упадёт — он увидит ошибку при следующей попытке.

# Запуск
print("RealVibeBot запущен. Ожидание сообщений...")
bot.polling(none_stop=True)