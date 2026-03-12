# main.py (расширенная версия)
import sys
from colorama import init, Fore, Style
from utils import (setup_logger, validate_input, format_timestamp,
                  save_to_file, load_from_file, retry_operation)
from config import config, db_config
import requests
import os

init(autoreset=True)
logger = setup_logger()

def display_banner():
    """Отображение баннера приложения"""
    banner = f"""
{Fore.CYAN}╔════════════════════════════════════╗
║ {config.APP_NAME} v{config.VERSION} ║
║ Enhanced Edition with File I/O ║
╚════════════════════════════════════╝{Style.RESET_ALL}
"""
    print(banner)

def fetch_data(api_url):
    """Получение данных из API с повторными попытками"""
    def fetch_operation():
        response = requests.get(api_url, timeout=config.TIMEOUT)
        response.raise_for_status()
        return response.json()
    
    try:
        data = retry_operation(fetch_operation)
        if data:
            logger.info(f"Data fetched successfully from {api_url}")
            # Автоматическое сохранение
            filename = f"api_data_{format_timestamp().replace(' ', '_')}.json"
            save_to_file(data, filename)
        return data
    except Exception as e:
        logger.error(f"Failed to fetch data after retries: {e}")
        return None

def process_user_input():
    """Обработка пользовательского ввода"""
    print(f"{Fore.YELLOW}Enter your data (name:age):{Style.RESET_ALL}")
    user_input = input().strip()
    
    try:
        name, age = user_input.split(':')
        data = {'name': name, 'age': int(age)}
        validate_input(data, ['name', 'age'])
        
        if int(age) < 0 or int(age) > 150:
            raise ValueError("Age must be between 0 and 150")
        
        print(f"{Fore.GREEN}✓ Valid input at {format_timestamp()}{Style.RESET_ALL}")
        
        # Сохраняем данные пользователя
        filename = f"user_{format_timestamp().replace(' ', '_')}.json"
        save_to_file(data, filename)
        
        return data
    except (ValueError, IndexError, TypeError) as e:
        print(f"{Fore.RED}✗ Error: {e}{Style.RESET_ALL}")
        return None

def load_previous_data():
    """Загрузка предыдущих данных"""
    json_files = [f for f in os.listdir('.') if f.startswith('user_') and f.endswith('.json')]
    if json_files:
        latest_file = max(json_files, key=os.path.getctime)
        data = load_from_file(latest_file)
        if data:
            print(f"{Fore.CYAN}Loaded previous data: {data}{Style.RESET_ALL}")
        return data
    return None

def main():
    """Главная функция"""
    display_banner()
    logger.info("Enhanced application started")
    
    # Загрузка предыдущих данных
    load_previous_data()
    
    # Тестовые данные
    test_api = "https://jsonplaceholder.typicode.com/todos/1"
    api_data = fetch_data(test_api)
    if api_data:
        print(f"{Fore.GREEN}API Test: {api_data}{Style.RESET_ALL}")
    
    # Обработка пользовательского ввода
    user_data = process_user_input()
    if user_data:
        print(f"{Fore.MAGENTA}Processed data: {user_data}{Style.RESET_ALL}")
    
    logger.info("Application finished")

if __name__ == "__main__":
    main()
