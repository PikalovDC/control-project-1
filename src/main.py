import json

import pandas as pd

from src.logging_config import setup_logging
from src.reports import spending_by_category
from src.services import get_cashback_analysis
from src.utils import load_excel_transactions
from src.views import get_main_page_data


def main():
    """Главный модуль для выполнения всех функциональностей проекта"""

    # Инициализация логирования
    setup_logging()

    # Загрузка данных из Excel
    transactions_list = load_excel_transactions("2021-12-01", "2021-12-31")

    if not transactions_list:
        print("Нет данных для анализа")
        return

    # Конвертируем в DataFrame для reports модуля
    df_transactions = pd.DataFrame(transactions_list)

    # 1. Основная функциональность - главная страница
    main_page_data = get_main_page_data("2021-12-15 14:30:00")

    # 2. Анализ кешбэка по категориям
    cashback_json = get_cashback_analysis(transactions_list, 2021, 12)

    print("ДАННЫЕ ГЛАВНОЙ СТРАНИЦЫ:")
    print(json.dumps(main_page_data, ensure_ascii=False, indent=2))

    print("\nАНАЛИЗ КЕШБЭКА ПО КАТЕГОРИЯМ:")
    print(cashback_json)

    # 3. ОТЧЕТЫ ПО КАТЕГОРИЯМ
    print("\nОТЧЕТЫ ПО КАТЕГОРИЯМ:")
    print("=" * 50)

    # Получаем все уникальные категории
    categories = df_transactions['category'].unique()

    for category in categories[:3]:  # Первые 3 категории
        print(f"\nКатегория: {category}")

        # Создаем отчет
        report_df = spending_by_category(df_transactions, category, "2021-12-31")

        # Выводим результат
        if len(report_df) > 0:
            report_json = report_df.to_json(orient='records', indent=2, force_ascii=False)
            print(f"Траты за последние 3 месяца: {len(report_df)} транзакций")
            print(report_json)
        else:
            print("Нет трат за последние 3 месяца")

    # Сохранение результатов
    with open('cashback_analysis.json', 'w', encoding='utf-8') as f:
        f.write(cashback_json)

    with open('main_page_data.json', 'w', encoding='utf-8') as f:
        json.dump(main_page_data, f, ensure_ascii=False, indent=2)

    print("\nРезультаты сохранены в файлы:")
    print("- cashback_analysis.json")
    print("- main_page_data.json")
    print("- report_*.json (отчеты по категориям)")


if __name__ == "__main__":
    main()
