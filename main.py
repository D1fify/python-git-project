# main.py

import sys
from colorama import init, Fore, Style
from utils import setup_logger, validate_input, format_timestamp
from config import config, db_config, api_config
import requests

# Инициализация colorama для цветного вывода
init(autoreset=True)

# Настраиваем логгер
logger = setup_logger()


def display_banner():
    """Красивый баннер приложения"""
    banner = f"""
{Fore.CYAN}╔════════════════════════════════════╗
║ {config.APP_NAME} v{config.VERSION} ║
║     🚀 Главный модуль приложения     ║
╚════════════════════════════════════╝{Style.RESET_ALL}
"""
    print(banner)
    logger.info(f"Баннер отображён, DEBUG режим: {config.DEBUG}")


def fetch_data(api_url):
    """Получение данных с API"""
    try:
        logger.info(f"Запрос к API: {api_url}")
        response = requests.get(api_url, timeout=config.TIMEOUT)
        response.raise_for_status()

        data = response.json()
        logger.info(f"✅ Данные получены, статус: {response.status_code}")
        return data

    except requests.Timeout:
        logger.error("⏰ Таймаут запроса")
        return None
    except requests.ConnectionError:
        logger.error("🔌 Ошибка подключения")
        return None
    except requests.RequestException as e:
        logger.error(f"❌ Ошибка запроса: {e}")
        return None


def process_user_input():
    """Обработка пользовательского ввода"""
    print(f"\n{Fore.YELLOW}📝 Введите данные в формате: имя:возраст{Style.RESET_ALL}")
    print(f"{Fore.CYAN}Пример: Иван:25{Style.RESET_ALL}")

    user_input = input("→ ").strip()

    try:
        # Разбиваем строку
        name, age = user_input.split(':')

        # Создаём словарь с данными
        data = {
            'name': name.strip(),
            'age': int(age.strip())
        }

        # Валидируем через utils.py
        validate_input(data, ['name', 'age'])

        # Дополнительная проверка возраста
        if data['age'] < 0 or data['age'] > 150:
            raise ValueError("Возраст должен быть от 0 до 150")

        print(f"{Fore.GREEN}✅ Данные корректны!{Style.RESET_ALL}")
        logger.info(f"Пользователь ввёл: {data}")

        # Показываем информацию о подключении к БД
        print(f"{Fore.MAGENTA}💾 Строка подключения к БД: {db_config.get_connection_string()}{Style.RESET_ALL}")

        return data

    except ValueError as e:
        print(f"{Fore.RED}❌ Ошибка валидации: {e}{Style.RESET_ALL}")
        logger.error(f"Ошибка ввода: {e}")
        return None
    except Exception as e:
        print(f"{Fore.RED}❌ Неизвестная ошибка: {e}{Style.RESET_ALL}")
        logger.error(f"Неизвестная ошибка: {e}")
        return None


def test_database_config():
    """Тестируем конфигурацию БД"""
    print(f"\n{Fore.CYAN}🔧 Тестирование конфигурации:{Style.RESET_ALL}")
    print(f"  • Приложение: {config.APP_NAME}")
    print(f"  • Версия: {config.VERSION}")
    print(f"  • Режим DEBUG: {config.DEBUG}")
    print(f"  • Максимум попыток: {config.MAX_RETRIES}")
    print(f"  • Таймаут: {config.TIMEOUT} сек")

    # Информация о БД
    print(f"\n{Fore.YELLOW}📊 Информация о БД:{Style.RESET_ALL}")
    print(f"  • Активная БД: {db_config.ACTIVE_DB}")
    print(f"  • PostgreSQL хост: {db_config.POSTGRES_HOST}")
    print(f"  • PostgreSQL порт: {db_config.POSTGRES_PORT}")
    print(f"  • PostgreSQL база: {db_config.POSTGRES_DB}")
    print(f"  • SQLite путь: {db_config.SQLITE_PATH}")

    # Строка подключения
    print(f"\n{Fore.GREEN}🔌 Строка подключения:{Style.RESET_ALL}")
    print(f"  {db_config.get_connection_string()}")

    # Информация об API
    print(f"\n{Fore.BLUE}🌐 Информация об API:{Style.RESET_ALL}")
    print(f"  • JSON Placeholder: {api_config.JSON_PLACEHOLDER_URL}")
    print(f"  • GitHub API: {api_config.GITHUB_API_URL}")
    print(f"  • Кэш TTL: {api_config.CACHE_TTL} сек")

    # Показываем полную конфигурацию БД
    print(f"\n{Fore.CYAN}📋 Полная конфигурация БД:{Style.RESET_ALL}")
    config_dict = db_config.get_config_dict()
    for key, value in config_dict.items():
        print(f"  • {key}: {value}")


def test_api():
    """Тестирование внешнего API"""
    print(f"\n{Fore.CYAN}🌐 Тестирование API...{Style.RESET_ALL}")

    # Используем JSON Placeholder API
    test_url = f"{api_config.JSON_PLACEHOLDER_URL}/todos/1"
    api_result = fetch_data(test_url)

    if api_result:
        print(f"{Fore.GREEN}✅ API ответ: {api_result}{Style.RESET_ALL}")

        # Проверяем структуру ответа
        if 'title' in api_result:
            print(f"{Fore.YELLOW}📌 Задача: {api_result['title']}{Style.RESET_ALL}")
        return True
    else:
        print(f"{Fore.YELLOW}⚠️ API недоступно, продолжаем без него{Style.RESET_ALL}")
        return False


def main():
    """Главная функция"""
    # Показываем баннер
    display_banner()

    # Тестируем конфиг
    test_database_config()

    # Создаём необходимые директории
    config.ensure_directories()
    print(f"\n{Fore.GREEN}✅ Директории созданы:{Style.RESET_ALL}")
    print(f"  • Логи: {config.LOG_DIR}")
    print(f"  • Данные: {config.DATA_DIR}")

    # Тест API
    test_api()

    # Основной цикл ввода
    print(f"\n{Fore.CYAN}🔄 Начинаем ввод данных пользователя{Style.RESET_ALL}")
    user_count = 0

    while True:
        # Обрабатываем ввод
        user_data = process_user_input()

        if user_data:
            user_count += 1
            print(f"{Fore.GREEN}✨ Обработанные данные #{user_count}: {user_data}{Style.RESET_ALL}")

            # Спрашиваем, хочет ли пользователь продолжить
            print(f"\n{Fore.CYAN}Продолжить? (y/n):{Style.RESET_ALL}")
            choice = input("→ ").lower().strip()
            if choice != 'y' and choice != 'yes':
                break
        else:
            # Если ошибка - пробуем снова
            print(f"{Fore.YELLOW}Попробуйте ещё раз{Style.RESET_ALL}")

    # Итог
    print(f"\n{Fore.GREEN}📊 Итог работы:{Style.RESET_ALL}")
    print(f"  • Обработано пользователей: {user_count}")
    print(f"  • Время работы: {format_timestamp()}")

    logger.info(f"👋 Приложение завершило работу. Обработано пользователей: {user_count}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}👋 Программа прервана пользователем{Style.RESET_ALL}")
        logger.info("Программа прервана (Ctrl+C)")
        sys.exit(0)
    except Exception as e:
        print(f"\n{Fore.RED}❌ Критическая ошибка: {e}{Style.RESET_ALL}")
        logger.error(f"Критическая ошибка: {e}")
        sys.exit(1)