#!/usr/bin/env python3
"""
Демо-версия Telegram-бота Synaplink
Позволяет протестировать логику без запуска Telegram API
"""

import asyncio
import logging
from config import Config
from openai_client import OpenAIClient
from application_handler import ApplicationHandler

# Настраиваем логирование
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DemoBot:
    """Демо-версия бота для тестирования"""
    
    def __init__(self):
        """Инициализация демо-бота"""
        self.openai_client = OpenAIClient()
        self.application_handler = ApplicationHandler()
        self.user_states = {}
        
    async def demo_conversation(self):
        """Демонстрирует работу бота"""
        print("🤖 Демо-версия бота Synaplink")
        print("=" * 50)
        
        # Демонстрация 1: Стартовое меню
        print("\n📱 ДЕМО 1: Стартовое меню")
        print("Пользователь нажимает /start")
        print("✅ Отправляется логотип:", Config.LOGO_IMAGE_URL)
        print("✅ Отправляется приветствие")
        print("✅ Показываются кнопки:")
        print("   - Подписаться на канал:", Config.TELEGRAM_CHANNEL_LINK)
        print("   - Начать диалог")
        
        # Демонстрация 2: Подписка на канал
        print("\n📢 ДЕМО 2: Подписка на канал")
        print("Пользователь переходит по ссылке:", Config.TELEGRAM_CHANNEL_LINK)
        print("✅ Пользователь подписывается на канал")
        
        # Демонстрация 3: Начало диалога
        print("\n💬 ДЕМО 3: Начало диалога")
        print("Пользователь нажимает 'Начать диалог'")
        print("✅ Ассистент приветствует пользователя")
        print("✅ Начинается диалог через OpenAI")
        
        # Демонстрация 4: Диалог с ассистентом
        print("\n🤖 ДЕМО 4: Диалог с ассистентом")
        test_messages = [
            "Привет! Расскажи о ваших услугах",
            "Какие технологии вы используете?",
            "Как начать сотрудничество?",
            "Меня зовут Иван, телефон +7 999 123-45-67, email ivan@example.com"
        ]
        
        for i, message in enumerate(test_messages, 1):
            print(f"\n   Сообщение {i}: {message}")
            try:
                # Имитируем ответ ассистента
                print("   ⏳ Обработка через OpenAI...")
                print("   ✅ Ассистент отвечает (имитация)")
            except Exception as e:
                print(f"   ❌ Ошибка: {e}")
        
        # Демонстрация 5: Формирование заявки
        print("\n📋 ДЕМО 5: Формирование заявки")
        sample_application = """
        [Заявка в рабочий чат]
        Имя: Иван Иванов
        Телефон: +7 999 123-45-67
        Email: ivan@example.com
        Запрос: Нужна консультация по разработке сайта и интеграции с CRM системой
        """
        
        print("   📝 Ассистент формирует заявку:")
        print(sample_application)
        
        # Проверяем обработку заявки
        is_valid = self.application_handler.is_application(sample_application)
        print(f"   ✅ Заявка определена как валидная: {is_valid}")
        
        # Форматируем для рабочего чата
        formatted = self.application_handler.format_application_for_working_chat(sample_application, 12345)
        print(f"   📤 Заявка отформатирована для рабочего чата:")
        print(f"   Длина: {len(formatted)} символов")
        
        # Демонстрация 6: Отправка в рабочий чат
        print("\n📤 ДЕМО 6: Отправка в рабочий чат")
        print(f"✅ Заявка отправляется в чат: {Config.WORKING_CHAT_ID}")
        print("✅ Менеджеры получают уведомление")
        print("✅ Пользователь получает подтверждение")
        
        # Демонстрация 7: Сброс разговора
        print("\n🔄 ДЕМО 7: Сброс разговора")
        print("Пользователь использует команду /reset")
        print("✅ Разговор сбрасывается")
        print("✅ Возврат к стартовому меню")
        
        print("\n" + "=" * 50)
        print("🎉 Демонстрация завершена!")
        
    def test_openai_connection(self):
        """Тестирует подключение к OpenAI"""
        print("\n🧪 Тестирование подключения к OpenAI...")
        try:
            # Проверяем конфигурацию
            print(f"   API Key: {Config.OPENAI_API_KEY[:20]}...")
            print(f"   Assistant ID: {Config.OPENAI_ASSISTANT_ID}")
            
            # Тестируем создание клиента
            client = OpenAIClient()
            print("   ✅ OpenAI клиент создан")
            
            # Тестируем создание thread (без реального API вызова)
            print("   ⚠️  Для полного тестирования нужен валидный токен бота")
            
            return True
            
        except Exception as e:
            print(f"   ❌ Ошибка: {e}")
            return False
    
    def test_application_handler(self):
        """Тестирует обработчик заявок"""
        print("\n🧪 Тестирование обработчика заявок...")
        try:
            handler = ApplicationHandler()
            
            # Тестовая заявка
            test_app = """
            [Заявка в рабочий чат]
            Имя: Тест Тестов
            Телефон: +7 999 999-99-99
            Email: test@example.com
            Запрос: Тестирование функциональности
            """
            
            # Проверяем определение заявки
            is_app = handler.is_application(test_app)
            print(f"   ✅ Заявка определена: {is_app}")
            
            # Проверяем парсинг
            parsed = handler.parse_application(test_app)
            if parsed:
                print(f"   ✅ Парсинг успешен: {len(parsed)} полей")
                for key, value in parsed.items():
                    if key != 'header':
                        print(f"      {key}: {value}")
            
            # Проверяем валидацию
            is_valid, message = handler.validate_application(test_app)
            print(f"   ✅ Валидация: {is_valid} - {message}")
            
            return True
            
        except Exception as e:
            print(f"   ❌ Ошибка: {e}")
            return False

async def main():
    """Основная функция демо"""
    print("🚀 Запуск демо-версии бота Synaplink")
    
    # Проверяем конфигурацию
    try:
        Config.validate()
        print("✅ Конфигурация проверена")
    except Exception as e:
        print(f"❌ Ошибка конфигурации: {e}")
        return
    
    # Создаем демо-бот
    demo_bot = DemoBot()
    
    # Тестируем компоненты
    demo_bot.test_application_handler()
    demo_bot.test_openai_connection()
    
    # Запускаем демонстрацию
    await demo_bot.demo_conversation()
    
    print("\n📝 Следующие шаги:")
    print("1. Создайте бота через @BotFather")
    print("2. Получите валидный токен")
    print("3. Обновите TELEGRAM_BOT_TOKEN в .env")
    print("4. Запустите бота командой: python bot.py")

if __name__ == "__main__":
    asyncio.run(main())
