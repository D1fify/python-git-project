#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Модуль конфигурации приложения.

Этот модуль содержит классы и функции для управления
конфигурацией приложения, включая загрузку из переменных
окружения и настройки по умолчанию.
"""

# config.py (обновленная версия для конфликта)
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    APP_NAME = "Python Git Project"
    VERSION = "1.2.0"  # Изменено для конфликта
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    MAX_RETRIES = 5    # Увеличено для конфликта
    TIMEOUT = 60       # Увеличено для конфликта
    DATA_DIR = os.getenv('DATA_DIR', './data')  # Новое поле

class DatabaseConfig:
    HOST = os.getenv('DB_HOST', 'localhost')
    PORT = int(os.getenv('DB_PORT', 5432))
    NAME = os.getenv('DB_NAME', 'myapp')
    USER = os.getenv('DB_USER', 'admin')
    PASSWORD = os.getenv('DB_PASSWORD', '')  # Новое поле
    
    @classmethod
    def get_connection_string(cls):
        if cls.PASSWORD:
            return f"postgresql://{cls.USER}:{cls.PASSWORD}@{cls.HOST}:{cls.PORT}/{cls.NAME}"
        return f"postgresql://{cls.USER}@{cls.HOST}:{cls.PORT}/{cls.NAME}"

config = Config()
db_config = DatabaseConfig()
