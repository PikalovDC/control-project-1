import json
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from src.utils import get_cards_data, get_greeting, get_month_range, get_top_transactions
from src.views import get_main_page_data


# Фикстуры для тестовых данных
@pytest.fixture
def sample_transactions():
    return [
        {
            'card_number': '1234',
            'amount': -1000.0,
            'date': '15.05.2024 12:00:00',
            'category': 'Супермаркет',
            'description': 'Пятерочка'
        },
        {
            'card_number': '1234',
            'amount': -500.0,
            'date': '16.05.2024 14:30:00',
            'category': 'Кафе',
            'description': 'Starbucks'
        },
        {
            'card_number': '5678',
            'amount': -2000.0,
            'date': '17.05.2024 10:15:00',
            'category': 'Транспорт',
            'description': 'Такси'
        }
    ]


@pytest.fixture
def sample_settings():
    return {
        "user_currencies": ["USD", "EUR"],
        "user_stocks": ["AAPL", "GOOGL"]
    }


@pytest.fixture
def mock_excel_data():
    return pd.DataFrame([
        {
            'Дата операции': '15.05.2024 12:00:00',
            'Номер карты': '*1234',
            'Сумма операции': -1000.0,
            'Категория': 'Супермаркет',
            'Описание': 'Пятерочка',
            'Статус': 'OK',
            'Валюта операции': 'RUB'
        },
        {
            'Дата операции': '16.05.2024 14:30:00',
            'Номер карты': '*1234',
            'Сумма операции': -500.0,
            'Категория': 'Кафе',
            'Описание': 'Starbucks',
            'Статус': 'OK',
            'Валюта операции': 'RUB'
        }
    ])


# Параметризованные тесты для get_greeting
@pytest.mark.parametrize("date_string,expected_greeting", [
    ("2024-05-15 08:00:00", "Доброе утро"),
    ("2024-05-15 14:00:00", "Добрый день"),
    ("2024-05-15 20:00:00", "Добрый вечер"),
    ("2024-05-15 02:00:00", "Доброй ночи"),
    ("invalid-date", "Добрый день")  # Тест на некорректную дату
])
def test_get_greeting(date_string, expected_greeting):
    assert get_greeting(date_string) == expected_greeting


# Параметризованные тесты для get_month_range
@pytest.mark.parametrize("date_string,expected_start,expected_end", [
    ("2024-05-15 12:00:00", "2024-05-01", "2024-05-15"),
    ("2024-12-31 23:59:59", "2024-12-01", "2024-12-31"),
])
def test_get_month_range(date_string, expected_start, expected_end):
    start, end = get_month_range(date_string)
    assert start == expected_start
    assert end == expected_end


def test_get_cards_data(sample_transactions):
    cards_data = get_cards_data(sample_transactions)

    assert len(cards_data) == 2
    assert cards_data[0]['last_digits'] == '1234'
    assert cards_data[0]['total_spent'] == 1500.0  # 1000 + 500
    assert cards_data[0]['cashback'] == 15.0  # 1500 / 100
    assert cards_data[1]['last_digits'] == '5678'
    assert cards_data[1]['total_spent'] == 2000.0


def test_get_top_transactions(sample_transactions):
    top_transactions = get_top_transactions(sample_transactions, limit=2)

    assert len(top_transactions) == 2
    # Должны быть отсортированы по убыванию суммы
    assert top_transactions[0]['amount'] == 2000.0
    assert top_transactions[1]['amount'] == 1000.0


@patch('src.views.get_greeting')
@patch('src.views.get_month_range')
@patch('src.views.load_excel_transactions')
@patch('src.views.get_cards_data')
@patch('src.views.get_top_transactions')
@patch('src.views.get_currency_rates')
@patch('src.views.get_stock_prices')
@patch('builtins.open')
def test_get_main_page_data_success(
        mock_open, mock_stocks, mock_currency, mock_top,
        mock_cards, mock_transactions, mock_range, mock_greeting,
        sample_transactions, sample_settings
):
    # Мокируем все зависимости
    mock_greeting.return_value = "Добрый день"
    mock_range.return_value = ("2024-05-01", "2024-05-15")
    mock_transactions.return_value = sample_transactions
    mock_cards.return_value = [{'last_digits': '1234', 'total_spent': 1500.0, 'cashback': 15.0}]
    mock_top.return_value = [{'date': '15.05.2024', 'amount': 1000.0, 'category': 'Test', 'description': 'Test'}]
    mock_currency.return_value = {"currency_rates": [{"currency": "USD", "rate": 75.50}]}
    mock_stocks.return_value = {"stock_prices": [{"stock": "AAPL", "price": 150.0}]}

    # Мокируем файл настроек
    mock_file = MagicMock()
    mock_open.return_value.__enter__.return_value = mock_file
    mock_file.read.return_value = json.dumps(sample_settings)

    result = get_main_page_data("2024-05-15 12:00:00")

    assert result["greeting"] == "Добрый день"
    assert len(result["cards"]) == 1
    assert len(result["top_transactions"]) == 1
    assert len(result["currency_rates"]) == 1
    assert len(result["stock_prices"]) == 1


@patch('src.views.get_greeting')
@patch('src.views.get_month_range')
@patch('src.views.load_excel_transactions')
@patch('builtins.open')
def test_get_main_page_data_error(mock_open, mock_transactions, mock_range, mock_greeting):
    # Мокируем исключение
    mock_greeting.side_effect = Exception("Test error")

    result = get_main_page_data("2024-05-15 12:00:00")

    # Должны получить пустые данные при ошибке
    assert result["greeting"] == "Добрый день"
    assert result["cards"] == []
    assert result["top_transactions"] == []
    assert result["currency_rates"] == []
    assert result["stock_prices"] == []


@patch('pandas.read_excel')
@patch('os.path.exists')
def test_load_excel_transactions_success(mock_exists, mock_read_excel, mock_excel_data):
    mock_exists.return_value = True
    mock_read_excel.return_value = mock_excel_data

    from src.utils import load_excel_transactions
    transactions = load_excel_transactions("2024-05-01", "2024-05-31")

    assert len(transactions) == 2
    assert transactions[0]['card_number'] == '1234'
    assert transactions[0]['amount'] == -1000.0


@patch('os.path.exists')
def test_load_excel_transactions_file_not_found(mock_exists):
    mock_exists.return_value = False

    from src.utils import load_excel_transactions
    transactions = load_excel_transactions("2024-05-01", "2024-05-31")

    assert transactions == []
