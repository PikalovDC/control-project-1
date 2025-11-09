import pandas as pd
import pytest

from src.reports import spending_by_category


@pytest.fixture
def sample_transactions_df():
    """Фикстура с тестовыми данными в формате DataFrame"""
    data = {
        'date': [
            '15.01.2024 12:00:00',  # 3 месяца назад от 15.04.2024
            '15.02.2024 14:30:00',  # 2 месяца назад
            '15.03.2024 10:15:00',  # 1 месяц назад
            '15.04.2024 09:00:00',  # текущий месяц
            '15.05.2024 11:00:00',  # будущий месяц (не должен попасть)
        ],
        'category': [
            'Food',
            'Food',
            'Transport',
            'Food',
            'Food'
        ],
        'amount': [
            -1000.0,
            -1500.0,
            -500.0,
            -2000.0,
            -1200.0
        ],
        'description': [
            'Grocery',
            'Restaurant',
            'Taxi',
            'Supermarket',
            'Cafe'
        ]
    }
    return pd.DataFrame(data)


@pytest.fixture
def transactions_with_income():
    """Фикстура с доходами и расходами"""
    data = {
        'date': [
            '15.03.2024 12:00:00',
            '20.03.2024 14:30:00',
            '25.03.2024 10:15:00',
        ],
        'category': [
            'Food',
            'Salary',
            'Food'
        ],
        'amount': [
            -1000.0,  # расход
            50000.0,  # доход (не должен попасть)
            -1500.0  # расход
        ],
        'description': [
            'Grocery',
            'Monthly salary',
            'Restaurant'
        ]
    }
    return pd.DataFrame(data)


def test_spending_by_category_no_transactions(sample_transactions_df):
    """Тест когда нет транзакций по указанной категории"""
    result = spending_by_category(sample_transactions_df, 'Entertainment', '2024-04-15')

    assert len(result) == 0
    assert isinstance(result, pd.DataFrame)


def test_spending_by_category_different_date(sample_transactions_df):
    """Тест с разными датами"""
    # Для даты 2024-03-15 должны найтись 2 транзакции
    result = spending_by_category(sample_transactions_df, 'Food', '2024-03-15')

    assert len(result) == 2
    assert all(result['category'] == 'Food')


def test_spending_by_category_only_expenses(transactions_with_income):
    """Тест что учитываются только расходы (отрицательные суммы)"""
    result = spending_by_category(transactions_with_income, 'Food', '2024-03-30')

    # Должны найтись только 2 расходные транзакции по Food
    assert len(result) == 2
    assert all(result['amount'] < 0)
    assert all(result['category'] == 'Food')

    # Доход не должен попасть в результат
    assert 'Salary' not in result['category'].values


def test_spending_by_category_wrong_category(sample_transactions_df):
    """Тест с несуществующей категорией"""
    result = spending_by_category(sample_transactions_df, 'NonExistentCategory', '2024-04-15')

    assert len(result) == 0
    assert isinstance(result, pd.DataFrame)


def test_spending_by_category_dataframe_structure(sample_transactions_df):
    """Тест структуры возвращаемого DataFrame"""
    result = spending_by_category(sample_transactions_df, 'Food', '2024-04-15')

    # Проверяем что все нужные колонки присутствуют
    expected_columns = ['date', 'category', 'amount', 'description']
    assert all(col in result.columns for col in expected_columns)

    # Проверяем что временная колонка удалена
    assert 'date_dt' not in result.columns
