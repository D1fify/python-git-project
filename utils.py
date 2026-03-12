#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Модуль вспомогательных функций.

Содержит утилиты для логирования, валидации, работы с данными
и другие общие функции, используемые в приложении.
"""
# utils.py (расширенная версия)
import logging
from datetime import datetime
import json
from config import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(config.APP_NAME)

def setup_logger():
    """Настройка логирования"""
    logger.info(f"Starting {config.APP_NAME} v{config.VERSION}")
    return logger

def validate_input(data, required_fields):
    """Валидация входных данных"""
    if not isinstance(data, dict):
        raise TypeError("Data must be a dictionary")
    
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        raise ValueError(f"Missing fields: {missing_fields}")
    
    # Дополнительная валидация типов
    for field, value in data.items():
        if field == 'age' and not isinstance(value, (int, float)):
            raise TypeError(f"Field '{field}' must be numeric")
    
    return True

def format_timestamp():
    """Форматирование временной метки"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def save_to_file(data, filename):
    """Сохранение данных в файл"""
    try:
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        logger.info(f"Data saved to {filename}")
        return True
    except Exception as e:
        logger.error(f"Failed to save data: {e}")
        return False

def load_from_file(filename):
    """Загрузка данных из файла"""
    try:
        with open(filename, 'r') as f:
            data = json.load(f)
        logger.info(f"Data loaded from {filename}")
        return data
    except Exception as e:
        logger.error(f"Failed to load data: {e}")
        return None

def retry_operation(operation, max_retries=config.MAX_RETRIES):
    """Повтор операции при ошибке"""
    for attempt in range(max_retries):
        try:
            return operation()
        except Exception as e:
            logger.warning(f"Attempt {attempt + 1} failed: {e}")
            if attempt == max_retries - 1:
                raise
    return None
