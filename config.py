"""
Модуль конфигурации для Telegram-бота Synaplink
Загружает все необходимые переменные окружения
"""

import os
from dotenv import load_dotenv

# Загружаем переменные окружения из .env файла
load_dotenv()

class Config:
	"""Класс конфигурации с настройками бота"""
	
	# Telegram Bot Token
	TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
	
	# OpenAI API Key
	OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
	
	# OpenAI Assistant ID
	OPENAI_ASSISTANT_ID = os.getenv('OPENAI_ASSISTANT_ID')
	
	# Telegram Channel Link
	TELEGRAM_CHANNEL_LINK = os.getenv('TELEGRAM_CHANNEL_LINK')
	
	# Telegram Working Chat ID (для отправки заявок)
	WORKING_CHAT_ID = os.getenv('WORKING_CHAT_ID')
	
	# Logo Image URL или путь к файлу
	LOGO_IMAGE_URL = os.getenv('LOGO_IMAGE_URL')

	# Checklist file URL (PDF)
	CHECKLIST_URL = os.getenv('CHECKLIST_URL')
	
	@classmethod
	def validate(cls):
		"""Проверяет, что все необходимые переменные окружения установлены"""
		required_vars = [
			'TELEGRAM_BOT_TOKEN',
			'OPENAI_API_KEY', 
			'OPENAI_ASSISTANT_ID',
			'WORKING_CHAT_ID',
			'LOGO_IMAGE_URL'
		]
		
		missing_vars = []
		for var in required_vars:
			if not getattr(cls, var):
				missing_vars.append(var)
		
		if missing_vars:
			raise ValueError(f"Отсутствуют обязательные переменные окружения: {', '.join(missing_vars)}")
		
		return True
