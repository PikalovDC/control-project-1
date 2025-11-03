import json
import logging
from typing import Any, Dict

from src.external_api import get_currency_rates, get_stock_prices
from src.logging_config import setup_logging
from src.utils import get_cards_data, get_greeting, get_month_range, get_top_transactions, load_excel_transactions

# Инициализируем логирование при импорте модуля
setup_logging()

# Создаем логгер для этого модуля
logger = logging.getLogger('views')


def get_main_page_data(date_string: str) -> Dict[str, Any]:
    """
    Генерирует JSON-ответ для главной страницы.
    Принимает: строку с датой в формате 'YYYY-MM-DD HH:MM:SS'
    Возвращает: JSON согласно ТЗ
    """
    try:
        logger.info(f"Начало формирования данных для даты: {date_string}")

        # Приветствие по времени суток
        greeting = get_greeting(date_string)

        # Получаем диапазон дат с 1 числа месяца по указанную дату
        start_date, end_date = get_month_range(date_string)

        # Загружаем и фильтруем транзакции из Excel
        transactions = load_excel_transactions(start_date, end_date)

        # Подготавливаем данные для JSON
        cards_data = get_cards_data(transactions)
        top_transactions = get_top_transactions(transactions)

        # Загружаем настройки пользователя
        with open('../data/user_settings.json', 'r', encoding='utf-8') as f:
            settings = json.load(f)

        # Получаем данные из API
        currency_data = get_currency_rates(settings.get('user_currencies', ['USD', 'EUR']))
        stocks_data = get_stock_prices(settings.get('user_stocks', ['AAPL', 'AMZN', 'GOOGL', 'MSFT', 'TSLA']))

        # Собираем финальный JSON
        result = {
            "greeting": greeting,
            "cards": cards_data,
            "top_transactions": top_transactions
        }
        result.update(currency_data)
        result.update(stocks_data)

        logger.info("Успешно сформированы данные для главной страницы")
        return result

    except Exception as e:
        logger.error(f"Критическая ошибка в get_main_page_data: {e}")
        # Возвращаем пустые данные
        return {
            "greeting": "Добрый день",
            "cards": [],
            "top_transactions": [],
            "currency_rates": [],
            "stock_prices": []
        }
