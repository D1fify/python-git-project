#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Модуль конфигурации приложения.

Этот модуль содержит классы и функции для управления
конфигурацией приложения, включая загрузку из переменных
окружения и настройки по умолчанию.
"""
# config.py (после разрешения конфликта)
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    APP_NAME = "Python Git Project"
    VERSION = "1.2.0"  # Берем из feature/enhancements (более новая)
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    MAX_RETRIES = 5    # Берем из feature/enhancements
    TIMEOUT = 60       # Берем из feature/enhancements
    DATA_DIR = os.getenv('DATA_DIR', './data')  # Из feature/enhancements
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')  # Добавляем из hotfix

class DatabaseConfig:
    HOST = os.getenv('DB_HOST', 'localhost')
    PORT = int(os.getenv('DB_PORT', 5432))
    NAME = os.getenv('DB_NAME', 'myapp')
    USER = os.getenv('DB_USER', 'admin')
    PASSWORD = os.getenv('DB_PASSWORD', '')  # Из feature/enhancements
    
    @classmethod
    def get_connection_string(cls):
        if cls.PASSWORD:
            return f"postgresql://{cls.USER}:{cls.PASSWORD}@{cls.HOST}:{cls.PORT}/{cls.NAME}"
        return f"postgresql://{cls.USER}@{cls.HOST}:{cls.PORT}/{cls.NAME}"

config = Config()
db_config = DatabaseConfig()
