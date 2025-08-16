"""
Модуль для работы с OpenAI API и ассистентом
Обрабатывает диалоги и формирует заявки
"""

import openai
from openai import OpenAI
from config import Config
import logging

# Настраиваем логирование
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OpenAIClient:
    """Класс для работы с OpenAI API"""
    
    def __init__(self):
        """Инициализация клиента OpenAI"""
        self.client = OpenAI(api_key=Config.OPENAI_API_KEY)
        self.assistant_id = Config.OPENAI_ASSISTANT_ID
        self.threads = {}  # Хранит thread_id для каждого пользователя
        
    def create_thread(self, user_id: int):
        """Создает новый thread для пользователя"""
        try:
            thread = self.client.beta.threads.create()
            self.threads[user_id] = thread.id
            logger.info(f"Создан новый thread {thread.id} для пользователя {user_id}")
            return thread.id
        except Exception as e:
            logger.error(f"Ошибка при создании thread: {e}")
            raise
    
    def get_or_create_thread(self, user_id: int):
        """Получает существующий thread или создает новый"""
        if user_id not in self.threads:
            return self.create_thread(user_id)
        return self.threads[user_id]
    
    def send_message(self, user_id: int, message: str):
        """
        Отправляет сообщение ассистенту и получает ответ
        
        Args:
            user_id: ID пользователя Telegram
            message: Текст сообщения пользователя
            
        Returns:
            str: Ответ ассистента
        """
        try:
            thread_id = self.get_or_create_thread(user_id)
            
            # Добавляем сообщение пользователя в thread
            self.client.beta.threads.messages.create(
                thread_id=thread_id,
                role="user",
                content=message
            )
            
            # Запускаем ассистента
            run = self.client.beta.threads.runs.create(
                thread_id=thread_id,
                assistant_id=self.assistant_id
            )
            
            # Ждем завершения выполнения
            while True:
                run_status = self.client.beta.threads.runs.retrieve(
                    thread_id=thread_id,
                    run_id=run.id
                )
                
                if run_status.status == 'completed':
                    break
                elif run_status.status == 'failed':
                    logger.error(f"Ошибка выполнения ассистента: {run_status.last_error}")
                    return "Извините, произошла ошибка. Попробуйте позже."
                
                import time
                time.sleep(1)
            
            # Получаем ответ ассистента
            messages = self.client.beta.threads.messages.list(thread_id=thread_id)
            
            # Ищем последнее сообщение ассистента
            for msg in messages.data:
                if msg.role == "assistant":
                    # Проверяем, содержит ли сообщение заявку
                    content = msg.content[0].text.value if msg.content else ""
                    if self._is_application(content):
                        return self._format_application(content)
                    return content
            
            return "Извините, не удалось получить ответ от ассистента."
            
        except Exception as e:
            logger.error(f"Ошибка при отправке сообщения: {e}")
            return "Произошла ошибка. Попробуйте позже."
    
    def _is_application(self, content: str) -> bool:
        """Проверяет, содержит ли сообщение заявку"""
        application_indicators = [
            "[Заявка в рабочий чат]",
            "Имя:",
            "Телефон:",
            "Email:",
            "Запрос:"
        ]
        
        return all(indicator in content for indicator in application_indicators)
    
    def _format_application(self, content: str) -> str:
        """Форматирует заявку для отправки в рабочий чат"""
        # Убираем лишние пробелы и форматируем
        lines = content.strip().split('\n')
        formatted_lines = []
        
        for line in lines:
            line = line.strip()
            if line:
                formatted_lines.append(line)
        
        return '\n'.join(formatted_lines)
    
    def reset_conversation(self, user_id: int):
        """Сбрасывает разговор для пользователя"""
        if user_id in self.threads:
            del self.threads[user_id]
            logger.info(f"Разговор сброшен для пользователя {user_id}")
