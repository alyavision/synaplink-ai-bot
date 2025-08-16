"""
Основной файл Telegram-бота для компании Synaplink
Обрабатывает команды, сообщения и интегрируется с OpenAI ассистентом
"""

import logging
import re
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, 
    CommandHandler, 
    MessageHandler, 
    CallbackQueryHandler,
    filters,
    ContextTypes
)
from config import Config
from openai_client import OpenAIClient
from application_handler import ApplicationHandler
import requests
from io import BytesIO

# Настраиваем логирование
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class SynaplinkBot:
    """Основной класс Telegram-бота Synaplink"""
    
    def __init__(self):
        """Инициализация бота"""
        try:
            logger.info("🔧 Инициализация бота...")
            logger.info(f"🔑 Создание Application с токеном: {Config.TELEGRAM_BOT_TOKEN[:10]}...")
            
            self.application = Application.builder().token(Config.TELEGRAM_BOT_TOKEN).build()
            logger.info("✅ Application создан успешно")
            
            logger.info("🤖 Создание OpenAI клиента...")
            self.openai_client = OpenAIClient()
            logger.info("✅ OpenAI клиент создан")
            
            logger.info("📋 Создание ApplicationHandler...")
            self.application_handler = ApplicationHandler()
            logger.info("✅ ApplicationHandler создан")
            
            self.user_states = {}  # Хранит состояние пользователей
            logger.info("✅ Словарь состояний пользователей инициализирован")
            
            # Регистрируем обработчики
            logger.info("🔧 Регистрация обработчиков...")
            self._setup_handlers()
            logger.info("✅ Инициализация бота завершена")
            
        except Exception as e:
            logger.error(f"❌ Ошибка при инициализации бота: {e}")
            import traceback
            logger.error(f"🔍 Stack trace: {traceback.format_exc()}")
            raise
        
    def _setup_handlers(self):
        """Настраивает все обработчики команд и сообщений"""
        
        logger.info("Настройка обработчиков...")
        
        # Обработчик команды /start
        self.application.add_handler(CommandHandler("start", self.start_command))
        logger.info("✅ Обработчик команды /start зарегистрирован")
        
        # Обработчик нажатий на inline кнопки
        self.application.add_handler(CallbackQueryHandler(self.button_callback))
        logger.info("✅ Обработчик кнопок CallbackQueryHandler зарегистрирован")
        
        # Обработчик текстовых сообщений
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        logger.info("✅ Обработчик текстовых сообщений зарегистрирован")
        
        # Обработчик команды /reset для сброса разговора
        self.application.add_handler(CommandHandler("reset", self.reset_command))
        logger.info("✅ Обработчик команды /reset зарегистрирован")
        
        logger.info("Все обработчики настроены успешно")
        
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /start - показывает стартовое меню"""
        logger.info("🚀 Команда /start вызвана!")
        user_id = update.effective_user.id if update.effective_user else None
        logger.info(f"👤 Пользователь ID: {user_id}")
        self.user_states[user_id] = "start"
        logger.info(f"✅ Состояние пользователя {user_id} установлено в 'start'")

        # Отправляем логотип
        try:
            logger.info("📸 Отправка логотипа...")
            if update.message:
                await self._send_logo(update, context)
            elif update.callback_query:
                await self._send_logo(update.callback_query, context)
            logger.info("✅ Логотип отправлен")
        except Exception as e:
            logger.error(f"❌ Ошибка при отправке логотипа: {e}")

        # Приветственное сообщение и кнопки
        welcome_text = (
            "🎉 Добро пожаловать в Synaplink AI!\n\n"
            "Мы - инновационная компания, специализирующаяся на разработке "
            "и внедрении передовых технологических решений.\n\n"
            "Наш ИИ-ассистент Сани готов ответить на все ваши вопросы "
            "и помочь с выбором оптимального решения для вашего бизнеса.\n\n"
            "Для начала работы подпишитесь на наш канал:"
        )
        keyboard = [
            [InlineKeyboardButton("📢 Подписаться на наш канал", url=Config.TELEGRAM_CHANNEL_LINK)],
            [InlineKeyboardButton("✅ Я подписался, начать диалог", callback_data="start_chat")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        try:
            logger.info("📝 Отправка приветственного сообщения...")
            if update.message:
                await update.message.reply_text(welcome_text, reply_markup=reply_markup)
            elif update.callback_query:
                await update.callback_query.message.reply_text(welcome_text, reply_markup=reply_markup)
            logger.info("✅ Приветственное сообщение отправлено")
        except Exception as e:
            logger.error(f"❌ Ошибка при отправке приветствия: {e}")
        
    async def _send_logo(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Отправляет логотип компании"""
        try:
            logger.info(f"🖼️ Попытка отправить логотип: {Config.LOGO_IMAGE_URL}")
            
            if Config.LOGO_IMAGE_URL.startswith('http'):
                # Если это URL, загружаем изображение
                logger.info("📥 Загрузка логотипа по URL")
                response = requests.get(Config.LOGO_IMAGE_URL)
                if response.status_code == 200:
                    photo = BytesIO(response.content)
                    await update.message.reply_photo(photo=photo, caption="🏢 Synaplink")
                    logger.info("✅ Логотип отправлен по URL")
                else:
                    logger.warning(f"⚠️ Ошибка загрузки логотипа: {response.status_code}")
                    await update.message.reply_text("🏢 Synaplink")
            else:
                # Если это путь к файлу
                logger.info("📁 Загрузка логотипа из файла")
                with open(Config.LOGO_IMAGE_URL, 'rb') as photo:
                    await update.message.reply_photo(photo=photo, caption="🏢 Synaplink")
                logger.info("✅ Логотип отправлен из файла")
        except Exception as e:
            logger.error(f"❌ Ошибка при отправке логотипа: {e}")
            await update.message.reply_text("🏢 Synaplink")
            logger.info("✅ Отправлен текстовый логотип")
    
    async def _is_user_subscribed(self, user_id: int) -> bool:
        """Проверяет, подписан ли пользователь на канал (только для публичных каналов)"""
        try:
            channel = Config.TELEGRAM_CHANNEL_LINK
            # Получаем username канала из ссылки
            if channel.startswith('https://t.me/'):
                channel_username = channel.split('https://t.me/')[-1].replace('/', '')
                if not channel_username.startswith('@'):
                    channel_username = '@' + channel_username
            else:
                channel_username = channel
            member = await self.application.bot.get_chat_member(channel_username, user_id)
            return member.status in ['member', 'administrator', 'creator']
        except Exception as e:
            logger.warning(f'Не удалось проверить подписку пользователя {user_id}: {e}')
            return False

    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик нажатий на inline кнопки"""
        logger.info("🔘 button_callback вызван!")
        query = update.callback_query
        logger.info(f"🔘 CallbackQuery получен: {query.data}")
        await query.answer()
        user_id = query.from_user.id
        logger.info(f"🔘 Обработка кнопки: {query.data} от пользователя {user_id}")
        if query.data == "start_chat":
            # Проверка подписки
            is_subscribed = await self._is_user_subscribed(user_id)
            if not is_subscribed:
                logger.info(f"❌ Пользователь {user_id} не подписан на канал!")
                await query.answer("Пожалуйста, подпишитесь на канал, чтобы продолжить.", show_alert=True)
                return
            logger.info(f"✅ Пользователь {user_id} подписан на канал, запускаем диалог")
            await self._start_chat(query, context)
        elif query.data == "reset_chat":
            logger.info(f"🔄 Сброс диалога для пользователя {user_id}")
            await self._reset_chat(query, context)
        else:
            logger.warning(f"⚠️ Неизвестная кнопка: {query.data}")
    
    async def _start_chat(self, query, context: ContextTypes.DEFAULT_TYPE):
        """Начинает диалог с ассистентом"""
        user_id = query.from_user.id
        # Меняем состояние пользователя
        self.user_states[user_id] = "chatting"
        # Больше не показываем никаких кнопок
        reply_markup = None
        # Отправляем служебный стартовый сигнал ассистенту
        try:
            initial_message = "Пользователь вернулся после подписки. Начни диалог, представься и спроси имя."
            response = self.openai_client.send_message(user_id, initial_message)
            welcome_message = (
                f"👋 Спасибо, что подписались на наш канал! 🎉\n\n"
                f"{response}"
            )
            await query.edit_message_text(welcome_message, reply_markup=reply_markup)
        except Exception as e:
            logger.error(f"Ошибка при инициации диалога: {e}")
            welcome_message = (
                "👋 Спасибо, что подписались на наш канал! 🎉\n\n"
                "Я готов помочь вам с любыми вопросами о наших услугах, "
                "технологиях и решениях. Представьтесь пожалуйста! И расскажите что Вас интересует."
            )
            await query.edit_message_text(welcome_message, reply_markup=reply_markup)
    
    async def _reset_chat(self, query, context: ContextTypes.DEFAULT_TYPE):
        """Сбрасывает разговор с ассистентом"""
        user_id = query.from_user.id
        
        # Сбрасываем разговор в OpenAI
        self.openai_client.reset_conversation(user_id)
        
        # Возвращаемся к стартовому меню
        self.user_states[user_id] = "start"
        
        await query.edit_message_text(
            "🔄 Разговор сброшен!\n\n"
            "Нажмите /start для начала нового диалога."
        )
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик текстовых сообщений от пользователя"""
        logger.info("📩 handle_message вызван!")
        user_id = update.effective_user.id if update.effective_user else None
        message_text = update.message.text if update.message else None
        logger.info(f"Пользователь: {user_id}, текст: {message_text}")

        # Проверяем состояние пользователя
        if user_id not in self.user_states or self.user_states[user_id] != "chatting":
            if update.message:
                await update.message.reply_text(
                    "Пожалуйста, начните с команды /start для начала работы с ботом."
                )
            return

        # Отправляем сообщение ассистенту OpenAI
        try:
            if update.message:
                await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
            response = self.openai_client.send_message(user_id, message_text)
            logger.info(f"Ответ ассистента: {response}")
            # Проверяем, содержит ли ответ ассистента финальный блок заявки
            is_final = self._contains_final_application(response)
            logger.info(f"Результат проверки финального блока: {is_final}")
            if is_final:
                logger.info("Пробую отправить заявку в рабочий чат...")
                await self._send_application_to_working_chat(context, response, user_id)
                if update.message:
                    await update.message.reply_text(response)
            else:
                if update.message:
                    await update.message.reply_text(response)
        except Exception as e:
            logger.error(f"Ошибка при обработке сообщения: {e}")
            if update.message:
                await update.message.reply_text(
                    "Извините, произошла ошибка. Попробуйте позже или используйте /reset для сброса."
                )
    

    
    def _contains_final_application(self, text: str) -> bool:
        """Проверяет, содержит ли текст финальный блок заявки по шаблону"""
        logger.info(f"Проверка на финальный блок. Текст ассистента:\n{text}")
        if not text:
            logger.info("❌ Текст пустой — не заявка")
            return False
        if "[Заявка в рабочий чат]" not in text:
            logger.info("❌ Нет заголовка [Заявка в рабочий чат] — не заявка")
            return False
        required_fields = ["Имя:", "Телефон:", "Телеграм:", "Запрос:"]
        for field in required_fields:
            if field not in text:
                logger.info(f"❌ Нет поля {field} — не заявка")
                return False
        logger.info("✅ Найден валидный финальный блок заявки!")
        return True
    

    
    def _get_current_time(self) -> str:
        """Возвращает текущее время в читаемом формате"""
        from datetime import datetime
        return datetime.now().strftime("%d.%m.%Y %H:%M:%S")
    
    async def _send_application_to_working_chat(self, context: ContextTypes.DEFAULT_TYPE, application_text: str, user_id: int):
        """Отправляет заявку в рабочий чат"""
        try:
            # Просто пересылаем блок заявки без изменений
            working_chat_message = (
                f"🚨 НОВАЯ ЗАЯВКА ОТ ПОЛЬЗОВАТЕЛЯ {user_id}\n\n"
                f"{application_text}"
            )
            
            # Отправляем в рабочий чат
            await context.bot.send_message(
                chat_id=Config.WORKING_CHAT_ID,
                text=working_chat_message
            )
            
            logger.info(f"Заявка от пользователя {user_id} отправлена в рабочий чат {Config.WORKING_CHAT_ID}")
            
        except Exception as e:
            logger.error(f"Ошибка при отправке заявки в рабочий чат: {e}")
            # Пытаемся отправить простой текст в случае ошибки
            try:
                simple_message = f"🚨 НОВАЯ ЗАЯВКА ОТ ПОЛЬЗОВАТЕЛЯ {user_id}\n\n{application_text}"
                await context.bot.send_message(
                    chat_id=Config.WORKING_CHAT_ID,
                    text=simple_message
                )
                logger.info(f"Заявка отправлена простым текстом")
            except Exception as e2:
                logger.error(f"Критическая ошибка при отправке заявки: {e2}")
    
    async def reset_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /reset - сбрасывает разговор"""
        user_id = update.effective_user.id
        
        # Сбрасываем разговор в OpenAI
        self.openai_client.reset_conversation(user_id)
        
        # Сбрасываем состояние пользователя
        self.user_states[user_id] = "start"
        
        await update.message.reply_text(
            "🔄 Разговор сброшен!\n\n"
            "Используйте /start для начала нового диалога."
        )
    
    def run(self):
        """Запускает бота"""
        try:
            # Проверяем конфигурацию
            logger.info("🔍 Проверка конфигурации...")
            Config.validate()
            logger.info("✅ Конфигурация проверена успешно")
            
            # Проверяем токен бота
            logger.info(f"🔑 Токен бота: {Config.TELEGRAM_BOT_TOKEN[:10]}...")
            
            # Запускаем бота
            logger.info("🚀 Запуск бота Synaplink...")
            logger.info("📡 Подключение к Telegram API...")
            
            # Добавляем обработчик ошибок
            self.application.add_error_handler(self._error_handler)
            
            # Запускаем с подробным логированием
            self.application.run_polling(
                allowed_updates=Update.ALL_TYPES,
                drop_pending_updates=True
            )
            
        except Exception as e:
            logger.error(f"❌ Критическая ошибка при запуске бота: {e}")
            logger.error(f"📋 Тип ошибки: {type(e).__name__}")
            import traceback
            logger.error(f"🔍 Stack trace: {traceback.format_exc()}")
            raise
    
    async def _error_handler(self, update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Обработчик ошибок"""
        logger.error(f"❌ Ошибка в боте: {context.error}")
        logger.error(f"📋 Тип ошибки: {type(context.error).__name__}")
        import traceback
        logger.error(f"🔍 Stack trace: {traceback.format_exc()}")
        
        # Если это ошибка подключения, логируем дополнительную информацию
        if hasattr(context.error, 'status_code'):
            logger.error(f"🌐 HTTP статус: {context.error.status_code}")
        if hasattr(context.error, 'response'):
            logger.error(f"📡 Ответ сервера: {context.error.response}")

if __name__ == "__main__":
    # Создаем и запускаем бота
    bot = SynaplinkBot()
    bot.run()
