#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Модуль конфигурации приложения.

Этот модуль содержит классы и функции для управления
конфигурацией приложения, включая загрузку из переменных
окружения и настройки по умолчанию.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Загружаем переменные окружения из .env файла
# Path(__file__).resolve().parent - директория, где находится config.py
env_path = Path(__file__).resolve().parent / '.env'
load_dotenv(dotenv_path=env_path)

class Config:
    """
    Основной класс конфигурации приложения.
    
    Содержит общие настройки, не зависящие от окружения.
    """
    
    # Основная информация о приложении
    APP_NAME = "Python Git Project"
    APP_DESCRIPTION = "Учебный проект для практики Git"
    VERSION = "1.0.0"
    
    # Режим отладки (по умолчанию False в production)
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    
    # Настройки производительности
    MAX_RETRIES = int(os.getenv('MAX_RETRIES', 3))  # Количество попыток при ошибках
    TIMEOUT = int(os.getenv('TIMEOUT', 30))         # Таймаут в секундах
    BATCH_SIZE = int(os.getenv('BATCH_SIZE', 100))  # Размер пакета при обработке
    
    # Пути к директориям
    BASE_DIR = Path(__file__).resolve().parent
    LOG_DIR = BASE_DIR / 'logs'
    DATA_DIR = BASE_DIR / 'data'
    
    # Логирование
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    LOG_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
    
    @classmethod
    def get_config_dict(cls):
        """
        Возвращает конфигурацию в виде словаря.
        
        Полезно для логирования или отладки.
        """
        return {
            'app_name': cls.APP_NAME,
            'version': cls.VERSION,
            'debug': cls.DEBUG,
            'max_retries': cls.MAX_RETRIES,
            'timeout': cls.TIMEOUT,
            'log_level': cls.LOG_LEVEL
        }
    
    @classmethod
    def ensure_directories(cls):
        """
        Создает необходимые директории, если они не существуют.
        """
        cls.LOG_DIR.mkdir(parents=True, exist_ok=True)
        cls.DATA_DIR.mkdir(parents=True, exist_ok=True)
        return True


class DatabaseConfig:
    """
    Конфигурация для подключения к базе данных.
    
    Содержит настройки для различных СУБД.
    """
    
    # PostgreSQL настройки
    POSTGRES_HOST = os.getenv('POSTGRES_HOST', 'localhost')
    POSTGRES_PORT = int(os.getenv('POSTGRES_PORT', 5432))
    POSTGRES_DB = os.getenv('POSTGRES_DB', 'myapp')
    POSTGRES_USER = os.getenv('POSTGRES_USER', 'postgres')
    POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD', '')
    
    # SQLite (для разработки)
    SQLITE_PATH = Config.BASE_DIR / 'app.db'
    
    # Выбор активной БД
    ACTIVE_DB = os.getenv('ACTIVE_DB', 'sqlite')  # sqlite или postgres
    
    @classmethod
    def get_connection_string(cls):
        """
        Возвращает строку подключения для активной БД.
        """
        if cls.ACTIVE_DB == 'postgres':
            if cls.POSTGRES_PASSWORD:
                return f"postgresql://{cls.POSTGRES_USER}:{cls.POSTGRES_PASSWORD}@{cls.POSTGRES_HOST}:{cls.POSTGRES_PORT}/{cls.POSTGRES_DB}"
            return f"postgresql://{cls.POSTGRES_USER}@{cls.POSTGRES_HOST}:{cls.POSTGRES_PORT}/{cls.POSTGRES_DB}"
        else:
            return f"sqlite:///{cls.SQLITE_PATH}"
    
    @classmethod
    def get_config_dict(cls):
        """
        Возвращает конфигурацию БД в виде словаря.
        """
        return {
            'active_db': cls.ACTIVE_DB,
            'postgres_host': cls.POSTGRES_HOST,
            'postgres_port': cls.POSTGRES_PORT,
            'postgres_db': cls.POSTGRES_DB,
            'sqlite_path': str(cls.SQLITE_PATH)
        }


class APIConfig:
    """
    Конфигурация для внешних API.
    """
    
    # Базовые URL для API
    JSON_PLACEHOLDER_URL = "https://jsonplaceholder.typicode.com"
    GITHUB_API_URL = "https://api.github.com"
    
    # Ключи API (из переменных окружения)
    API_KEY = os.getenv('API_KEY', '')
    API_SECRET = os.getenv('API_SECRET', '')
    
    # Настройки кэширования
    CACHE_TTL = int(os.getenv('CACHE_TTL', 300))  # 5 минут


# Создаем экземпляры конфигурации для удобного импорта
config = Config()
db_config = DatabaseConfig()
api_config = APIConfig()


def setup_config():
    """
    Функция для настройки конфигурации при запуске.
    
    Создает необходимые директории и проверяет наличие
    обязательных переменных окружения.
    """
    # Создаем директории
    Config.ensure_directories()
    
    # Проверяем наличие необходимых переменных в production
    if not Config.DEBUG:
        required_vars = []
        if db_config.ACTIVE_DB == 'postgres' and not db_config.POSTGRES_PASSWORD:
            required_vars.append('POSTGRES_PASSWORD')
        
        if required_vars:
            raise EnvironmentError(
                f"Missing required environment variables: {', '.join(required_vars)}"
            )
    
    return True


# Автоматически выполняем настройку при импорте
if __name__ != '__main__':
    setup_config()
