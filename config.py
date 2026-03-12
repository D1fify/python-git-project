#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Модуль конфигурации приложения.

Этот модуль содержит классы и функции для управления
конфигурацией приложения, включая загрузку из переменных
окружения и настройки по умолчанию.
"""
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    APP_NAME = "Python Git Project"
    VERSION = "1.3.0"  # Другая версия
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    MAX_RETRIES = 10   # Другое значение
    TIMEOUT = 120      # Другое значение
    API_ENDPOINT = os.getenv('API_ENDPOINT', 'https://api.example.com')  # Новое поле

class DatabaseConfig:
    HOST = os.getenv('DB_HOST', 'localhost')
    PORT = int(os.getenv('DB_PORT', 5432))
    NAME = os.getenv('DB_NAME', 'myapp')
    USER = os.getenv('DB_USER', 'admin')
    
    @classmethod
    def get_connection_string(cls):
        return f"postgresql://{cls.USER}@{cls.HOST}:{cls.PORT}/{cls.NAME}"

config = Config()
db_config = DatabaseConfig()
