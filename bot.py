import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.enums import ParseMode
from config_reader import config
import openai

# Настраиваем логирование, чтобы видеть важные сообщения в консоли
logging.basicConfig(level=logging.INFO)

# Инициализируем клиента для работы с API
client = openai.AsyncOpenAI(
    api_key=config.openrouter_api_key.get_secret_value(),
    base_url="https://openrouter.ai/api/v1"
)

# Создаем экземпляры бота и диспетчера для обработки входящих сообщений
bot = Bot(token=config.bot_token.get_secret_value(), default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=MemoryStorage())
# Храним историю диалогов для каждого чата
conversation_histories = {}
# Функция для отправки запроса к модели и обновления истории переписки
async def query_llm(prompt, history):
    # Добавляем сообщение пользователя в историю диалога
    history.append({"role": "user", "content": prompt})
    # Отправляем запрос к ИИ с заданными параметрами
    response = await client.chat.completions.create(
        model="gpt-4o",
        messages=history,
        max_tokens=150,
        temperature=0.5,
    )
    # Извлекаем и очищаем ответ модели
    answer = response.choices[0].message.content.strip()
    # Добавляем ответ модели в историю диалога
    history.append({"role": "assistant", "content": answer})
    return answer, history

# Обработчик команды /start — начинает диалог с ботом
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    # создаём историю для нового чата
    conversation_histories[message.chat.id] = []
    await message.answer(
        "👋 <b>Привет!</b>\n\n"
        "Я — ИИ-бот. Напиши что-нибудь, и я отвечу.\n\n"
        "Для очистки истории используй команду <b>/clear</b>."
    )

# Обработчик команды /help — выводит справочную информацию
@dp.message(Command("help"))
async def cmd_help(message: types.Message):
    # Создаем кнопку для связи с разработчиком
    keyboard = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [types.InlineKeyboardButton(text="Написать разработчику", url="https://t.me/kakaphonya")]
        ]
    )
    await message.answer(
        "❓ <b>Помощь</b>\n\n"
        "Если у тебя есть вопросы или предложения, нажми кнопку ниже.",
        reply_markup=keyboard
    )

# Обработчик команды /clear — очищает историю диалога в чате
@dp.message(Command("clear"))
async def cmd_clear(message: types.Message):
    chat_id = message.chat.id
    # Сбрасываем историю переписки для данного чата
    conversation_histories[chat_id] = []
    await message.answer("🗑 <b>История очищена!</b>\n\n"
                         "Напиши что-нибудь новое.")

# Обработчик текстовых сообщений — отвечает на любые текстовые запросы
@dp.message()
async def handle_text(message: types.Message):
    chat_id = message.chat.id
    # Убеждаемся, что для чата есть история сообщений
    conversation_histories.setdefault(chat_id, [])

    # Сообщаем челику, что запрос обрабатывается
    msg = await message.answer("<i>Обрабатываю запрос...</i>")

    try:
        # Получаем ответ от модели и обновляем историю диалога
        answer, conversation_histories[chat_id] = await query_llm(message.text, conversation_histories[chat_id])
        await message.answer(f"*Ответ:*\n\n{answer}", parse_mode="Markdown")
        # Удаляем ненужное сообщение
        await bot.delete_message(chat_id, msg.message_id)

    except Exception:
        # Логируем ошибку и уведомляем пользователя что что-то пошло не так(
        logging.exception("Ошибка при запросе к LLM:")
        await message.answer("⚠ <b>Произошла ошибка при обработке запроса.</b>")

# Основная функция для запуска бота
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
