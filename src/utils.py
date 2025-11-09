import logging
import os
from datetime import datetime
from typing import Any, Dict, List

import pandas as pd

# Создаем логгер для этого модуля
logger = logging.getLogger('utils')


def get_greeting(date_string: str) -> str:
    """
    Определяет приветствие по времени суток.
    Утро: 05:00-11:59, День: 12:00-17:59, Вечер: 18:00-22:59, Ночь: 23:00-04:59
    """
    try:
        dt = datetime.strptime(date_string, '%Y-%m-%d %H:%M:%S')
        hour = dt.hour

        if 5 <= hour < 12:
            greeting = "Доброе утро"
        elif 12 <= hour < 18:
            greeting = "Добрый день"
        elif 18 <= hour < 23:
            greeting = "Добрый вечер"
        else:
            greeting = "Доброй ночи"

        logger.info(f"Определено приветствие '{greeting}' для времени {hour}:00")
        return greeting

    except Exception as e:
        logger.error(f"Ошибка определения приветствия для '{date_string}': {e}")
        return "Добрый день"


def get_month_range(date_string: str) -> tuple[str, str]:
    """
    Возвращает диапазон дат с 1 числа месяца по указанную дату.
    """
    try:
        dt = datetime.strptime(date_string, '%Y-%m-%d %H:%M:%S')
        first_day = dt.replace(day=1)

        start_date = first_day.strftime('%Y-%m-%d')
        end_date = dt.strftime('%Y-%m-%d')

        logger.info(f"Диапазон дат: {start_date} - {end_date}")
        return start_date, end_date

    except Exception as e:
        logger.error(f"Ошибка определения диапазона дат для '{date_string}': {e}")
        today = datetime.now()
        first_day = today.replace(day=1)
        return first_day.strftime('%Y-%m-%d'), today.strftime('%Y-%m-%d')


def load_excel_transactions(start_date: str, end_date: str) -> List[Dict[str, Any]]:
    """
    Загружает транзакции из Excel файла и фильтрует по дате и статусу.
    """
    transactions = []
    excel_path = '../data/operations.xlsx'

    if not os.path.exists(excel_path):
        logger.error(f"Файл {excel_path} не найден!")
        return transactions

    try:
        df = pd.read_excel(excel_path)
        logger.info(f"Загружено {len(df)} строк из Excel")

        for _, row in df.iterrows():
            transaction = row.to_dict()

            if is_valid_transaction(transaction, start_date, end_date):
                standardized = standardize_transaction(transaction)
                transactions.append(standardized)

        logger.info(f"Отфильтровано {len(transactions)} транзакций за период {start_date} - {end_date}")
        return transactions

    except Exception as e:
        logger.error(f"Ошибка загрузки Excel: {e}")
        return []


def is_valid_transaction(transaction: Dict[str, Any], start_date: str, end_date: str) -> bool:
    """
    Проверяет валидность транзакции: статус OK и дата в диапазоне.
    """
    try:
        status = transaction.get('Статус', '')
        if status != 'OK':
            return False

        date_str = str(transaction.get('Дата операции', ''))
        if not date_str or date_str == 'nan':
            return False

        dt = datetime.strptime(date_str, '%d.%m.%Y %H:%M:%S')
        transaction_date = dt.strftime('%Y-%m-%d')

        is_valid = start_date <= transaction_date <= end_date
        if not is_valid:
            logger.debug(f"Транзакция {date_str} вне диапазона {start_date}-{end_date}")

        return is_valid

    except Exception as e:
        logger.debug(f"Невалидная транзакция: {e}")
        return False


def standardize_transaction(transaction: Dict[str, Any]) -> Dict[str, Any]:
    """
    Приводит транзакцию из Excel формата к единому формату.
    """
    try:
        standardized = {}

        date_str = str(transaction.get('Дата операции', ''))
        standardized['date'] = date_str

        card_number = str(transaction.get('Номер карты', ''))
        if card_number and card_number != 'nan' and card_number.startswith('*'):
            standardized['card_number'] = card_number[1:]
        else:
            standardized['card_number'] = ''

        amount = transaction.get('Сумма операции', 0)
        try:
            standardized['amount'] = float(amount)
        except (ValueError, TypeError):
            standardized['amount'] = 0.0

        category = str(transaction.get('Категория', ''))
        standardized['category'] = category if category != 'nan' else 'Разное'

        description = str(transaction.get('Описание', ''))
        standardized['description'] = description if description != 'nan' else ''

        currency = str(transaction.get('Валюта операции', 'RUB'))
        standardized['currency'] = currency if currency != 'nan' else 'RUB'

        return standardized

    except Exception as e:
        logger.error(f"Ошибка стандартизации транзакции: {e}")
        return {}


def get_cards_data(transactions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Рассчитывает данные по картам: последние цифры, сумма расходов, кешбэк.
    Кешбэк: 1 рубль на каждые 100 рублей расходов.
    """
    try:
        cards = {}

        for transaction in transactions:
            card_number = transaction.get('card_number', '')
            if not card_number or len(card_number) != 4:
                continue

            amount = transaction.get('amount', 0)

            if card_number not in cards:
                cards[card_number] = {
                    'last_digits': card_number,
                    'total_spent': 0.0,
                    'cashback': 0.0
                }

            if amount < 0:
                cards[card_number]['total_spent'] += abs(amount)

        for card in cards.values():
            card['cashback'] = card['total_spent'] / 100
            card['total_spent'] = round(card['total_spent'], 2)
            card['cashback'] = round(card['cashback'], 2)

        logger.info(f"Сформированы данные для {len(cards)} карт")
        return list(cards.values())

    except Exception as e:
        logger.error(f"Ошибка расчета данных по картам: {e}")
        return []


def get_top_transactions(transactions: List[Dict[str, Any]], limit: int = 5) -> List[Dict[str, Any]]:
    """
    Возвращает топ-N транзакций по сумме расходов.
    """
    try:
        expenses = [t for t in transactions if t.get('amount', 0) < 0]

        sorted_transactions = sorted(
            expenses,
            key=lambda x: abs(x.get('amount', 0)),
            reverse=True
        )

        top_transactions = []
        for transaction in sorted_transactions[:limit]:
            original_date = transaction.get('date', '')
            try:
                dt = datetime.strptime(original_date, '%d.%m.%Y %H:%M:%S')
                formatted_date = dt.strftime('%d.%m.%Y')
            except:
                formatted_date = original_date

            top_transactions.append({
                'date': formatted_date,
                'amount': abs(round(transaction.get('amount', 0), 2)),
                'category': transaction.get('category', ''),
                'description': transaction.get('description', '')
            })

        logger.info(f"Сформирован топ {len(top_transactions)} транзакций")
        return top_transactions

    except Exception as e:
        logger.error(f"Ошибка формирования топа транзакций: {e}")
        return []
