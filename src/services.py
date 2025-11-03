import json
import logging
from collections import defaultdict
from datetime import datetime
from typing import Any, Dict, List

# Настройка логгера
logger = logging.getLogger('services')


def analyze_cashback_categories(data: List[Dict[str, Any]], year: int, month: int) -> Dict[str, float]:
    """
    Анализирует выгодность категорий для повышенного кешбэка.
    Работает с данными из Excel файла.
    """

    logger.info(f"Начало анализа кешбэка за {month}.{year}, транзакций: {len(data)}")

    category_totals = defaultdict(float)

    for transaction in data:
        try:
            # Проверяем дату транзакции с помощью datetime
            date_str = transaction.get('date', '')
            if not date_str:
                continue

            # Используем datetime для парсинга даты
            dt = datetime.strptime(date_str, '%d.%m.%Y %H:%M:%S')
            if dt.year != year or dt.month != month:
                continue

            # Проверяем что это расход (отрицательная сумма)
            amount = transaction.get('amount', 0)
            if amount >= 0:
                continue

            # Суммируем расходы по категориям
            category = transaction.get('category', 'Разное')
            category_totals[category] += abs(amount)

        except Exception as e:
            logger.warning(f"Ошибка обработки транзакции: {e}")
            continue

    # Рассчитываем кешбэк (1% от суммы расходов)
    cashback_analysis = {
        category: round(amount * 0.01, 2)
        for category, amount in category_totals.items()
    }

    # Сортируем по убыванию кешбэка
    result = dict(sorted(cashback_analysis.items(), key=lambda x: x[1], reverse=True))

    logger.info(f"Анализ завершен. Найдено категорий: {len(result)}")
    return result


def get_cashback_analysis(data: List[Dict[str, Any]], year: int, month: int) -> str:
    """
    Возвращает анализ кешбэка в формате JSON.
    """
    logger.info(f"Формирование JSON отчета за {month}.{year}")
    analysis = analyze_cashback_categories(data, year, month)
    return json.dumps(analysis, ensure_ascii=False, indent=2)
