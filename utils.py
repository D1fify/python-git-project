#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Модуль вспомогательных функций.

Содержит утилиты для логирования, валидации, работы с данными
и другие общие функции, используемые в приложении.
"""

import logging
import sys
import json
import time
from datetime import datetime
from typing import Any, Dict, List, Optional, Union, Callable
from pathlib import Path
from functools import wraps
from config import config, db_config

# Настройка базового логирования
def setup_logger(name: str = None) -> logging.Logger:
    """
    Настройка и получение логгера.
    
    Args:
        name: Имя логгера (обычно __name__)
    
    Returns:
        logging.Logger: Настроенный логгер
    """
    # Создаем форматтер для логов
    formatter = logging.Formatter(
        fmt=config.LOG_FORMAT,
        datefmt=config.LOG_DATE_FORMAT
    )
    
    # Настраиваем обработчик для вывода в консоль
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    
    # Настраиваем обработчик для записи в файл
    log_file = config.LOG_DIR / f'app_{datetime.now().strftime("%Y%m%d")}.log'
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setFormatter(formatter)
    
    # Получаем или создаем логгер
    logger = logging.getLogger(name or config.APP_NAME)
    logger.setLevel(getattr(logging, config.LOG_LEVEL.upper()))
    
    # Удаляем существующие обработчики (чтобы избежать дублирования)
    logger.handlers.clear()
    
    # Добавляем обработчики
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    # Логируем запуск
    logger.info(f"Logger initialized for {config.APP_NAME} v{config.VERSION}")
    logger.debug(f"Log file: {log_file}")
    
    return logger


# Создаем глобальный логгер
logger = setup_logger(__name__)


def validate_input(data: Dict[str, Any], required_fields: List[str]) -> bool:
    """
    Валидация входных данных.
    
    Проверяет наличие обязательных полей и их типы.
    
    Args:
        data: Словарь с данными для проверки
        required_fields: Список обязательных полей
    
    Returns:
        bool: True если валидация прошла успешно
    
    Raises:
        TypeError: Если data не словарь или поля имеют неправильный тип
        ValueError: Если отсутствуют обязательные поля
    """
    # Проверяем тип данных
    if not isinstance(data, dict):
        raise TypeError(f"Data must be a dictionary, got {type(data).__name__}")
    
    # Проверяем наличие обязательных полей
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")
    
    # Дополнительная валидация типов для известных полей
    for field, value in data.items():
        if field == 'age' and value is not None:
            if not isinstance(value, (int, float)):
                raise TypeError(f"Field '{field}' must be numeric, got {type(value).__name__}")
            if value < 0 or value > 150:
                raise ValueError(f"Field '{field}' must be between 0 and 150")
        
        elif field == 'email' and value:
            if not isinstance(value, str):
                raise TypeError(f"Field '{field}' must be string")
            if '@' not in value:
                raise ValueError(f"Field '{field}' must be a valid email")
        
        elif field == 'name' and value:
            if not isinstance(value, str):
                raise TypeError(f"Field '{field}' must be string")
            if len(value.strip()) == 0:
                raise ValueError(f"Field '{field}' cannot be empty")
    
    logger.debug(f"Validation passed for fields: {required_fields}")
    return True


def format_timestamp(format: str = None) -> str:
    """
    Форматирование текущей временной метки.
    
    Args:
        format: Строка формата (по умолчанию из config)
    
    Returns:
        str: Отформатированная дата и время
    """
    if format is None:
        format = config.LOG_DATE_FORMAT
    
    return datetime.now().strftime(format)


def retry_operation(
    operation: Callable,
    max_retries: int = None,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: tuple = (Exception,)
) -> Any:
    """
    Повтор операции при возникновении ошибки.
    
    Args:
        operation: Функция для выполнения
        max_retries: Максимальное количество попыток
        delay: Начальная задержка между попытками
        backoff: Множитель увеличения задержки
        exceptions: Кортеж исключений для повторных попыток
    
    Returns:
        Any: Результат выполнения операции
    
    Raises:
        Exception: Последнее исключение после всех попыток
    """
    if max_retries is None:
        max_retries = config.MAX_RETRIES
    
    current_delay = delay
    last_exception = None
    
    for attempt in range(max_retries):
        try:
            logger.debug(f"Operation attempt {attempt + 1}/{max_retries}")
            result = operation()
            if attempt > 0:
                logger.info(f"Operation succeeded on attempt {attempt + 1}")
            return result
            
        except exceptions as e:
            last_exception = e
            if attempt < max_retries - 1:
                logger.warning(
                    f"Attempt {attempt + 1} failed: {e}. "
                    f"Retrying in {current_delay:.1f}s..."
                )
                time.sleep(current_delay)
                current_delay *= backoff
            else:
                logger.error(f"All {max_retries} attempts failed")
    
    raise last_exception


def retry_decorator(
    max_retries: int = None,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: tuple = (Exception,)
):
    """
    Декоратор для повторных попыток выполнения функции.
    
    Args:
        max_retries: Максимальное количество попыток
        delay: Начальная задержка
        backoff: Множитель увеличения задержки
        exceptions: Кортеж исключений для повторных попыток
    
    Returns:
        Callable: Декорированная функция
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            operation = lambda: func(*args, **kwargs)
            return retry_operation(
                operation,
                max_retries=max_retries,
                delay=delay,
                backoff=backoff,
                exceptions=exceptions
            )
        return wrapper
    return decorator


def save_json(data: Any, filename: Union[str, Path]) -> bool:
    """
    Сохранение данных в JSON файл.
    
    Args:
        data: Данные для сохранения
        filename: Имя файла или путь
    
    Returns:
        bool: True если сохранение успешно
    """
    try:
        # Преобразуем в Path если строка
        filepath = Path(filename)
        
        # Добавляем расширение .json если нет
        if not filepath.suffix:
            filepath = filepath.with_suffix('.json')
        
        # Создаем директорию если нужно
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        # Сохраняем данные
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False, default=str)
        
        logger.info(f"Data saved to {filepath}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to save data to {filename}: {e}")
        return False


def load_json(filename: Union[str, Path]) -> Optional[Any]:
    """
    Загрузка данных из JSON файла.
    
    Args:
        filename: Имя файла или путь
    
    Returns:
        Optional[Any]: Загруженные данные или None при ошибке
    """
    try:
        filepath = Path(filename)
        
        if not filepath.exists():
            logger.warning(f"File {filepath} does not exist")
            return None
        
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        logger.info(f"Data loaded from {filepath}")
        return data
        
    except Exception as e:
        logger.error(f"Failed to load data from {filename}: {e}")
        return None


def chunk_list(data: List[Any], chunk_size: int = None) -> List[List[Any]]:
    """
    Разбиение списка на части.
    
    Args:
        data: Исходный список
        chunk_size: Размер части (по умолчанию из config)
    
    Returns:
        List[List[Any]]: Список частей
    """
    if chunk_size is None:
        chunk_size = config.BATCH_SIZE
    
    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")
    
    return [data[i:i + chunk_size] for i in range(0, len(data), chunk_size)]


def get_system_info() -> Dict[str, Any]:
    """
    Получение информации о системе.
    
    Returns:
        Dict[str, Any]: Информация о системе
    """
    import platform
    import os
    
    return {
        'python_version': sys.version,
        'platform': platform.platform(),
        'processor': platform.processor(),
        'hostname': platform.node(),
        'cwd': str(Path.cwd()),
        'pid': os.getpid()
    }


# Тестирование функций при прямом запуске
if __name__ == '__main__':
    print("Testing utils module...")
    
    # Тест логирования
    test_logger = setup_logger("test")
    test_logger.info("Test log message")
    
    # Тест валидации
    test_data = {'name': 'John', 'age': 30, 'email': 'john@example.com'}
    try:
        validate_input(test_data, ['name', 'age'])
        print("✓ Validation test passed")
    except Exception as e:
        print(f"✗ Validation test failed: {e}")
    
    # Тест форматирования времени
    print(f"Current time: {format_timestamp()}")
    
    # Тест системной информации
    sys_info = get_system_info()
    print(f"System info: {sys_info['python_version'][:30]}...")
