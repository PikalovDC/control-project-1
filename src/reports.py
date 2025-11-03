import json
import logging
from datetime import datetime, timedelta
from functools import wraps
from typing import Optional

import pandas as pd

# Настройка логгера
logger = logging.getLogger('reports')


def report_to_file(func):
    """Декоратор без параметра - записывает отчет в файл с названием по умолчанию"""

    @wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)

        # Формируем имя файла по умолчанию
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"report_{func.__name__}_{timestamp}.json"

        # Сохраняем результат в файл
        if isinstance(result, pd.DataFrame):
            result.to_json(filename, orient='records', indent=2, force_ascii=False)
        else:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)

        logger.info(f"Отчет сохранен в файл: {filename}")
        return result

    return wrapper


@report_to_file
def spending_by_category(transactions: pd.DataFrame,
                         category: str,
                         date: Optional[str] = None) -> pd.DataFrame:
    """
    Возвращает траты по заданной категории за последние три месяца.
    Работает с данными из нашего Excel файла.
    """

    logger.info(f"Формирование отчета по категории '{category}'")

    # Если дата не передана, берем текущую дату
    if date is None:
        target_date = datetime.now()
    else:
        target_date = datetime.strptime(date, '%Y-%m-%d')

    # Вычисляем дату 3 месяца назад
    three_months_ago = target_date - timedelta(days=90)

    # Конвертируем даты в нашем формате (из DD.MM.YYYY HH:MM:SS в datetime)
    transactions['date_dt'] = pd.to_datetime(transactions['date'], format='%d.%m.%Y %H:%M:%S')

    # Фильтруем транзакции по категории и дате (только расходы)
    filtered_transactions = transactions[
        (transactions['category'] == category) &
        (transactions['amount'] < 0) &  # Только расходы
        (transactions['date_dt'] >= three_months_ago) &
        (transactions['date_dt'] <= target_date)
        ]

    # Убираем временную колонку
    result = filtered_transactions.drop('date_dt', axis=1)

    logger.info(f"Найдено {len(result)} транзакций по категории '{category}'")
    return result
