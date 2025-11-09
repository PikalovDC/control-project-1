import json

import pytest

from src.services import analyze_cashback_categories, get_cashback_analysis


@pytest.fixture
def sample_transactions():
    return [
        {
            'date': '15.05.2024 12:00:00',
            'category': 'Супермаркеты',
            'amount': -5000.0
        },
        {
            'date': '16.05.2024 14:30:00',
            'category': 'Кафе',
            'amount': -1500.0
        },
        {
            'date': '17.05.2024 10:15:00',
            'category': 'Супермаркеты',
            'amount': -3000.0
        },
        {
            'date': '18.05.2024 19:00:00',
            'category': 'Транспорт',
            'amount': -2000.0
        },
        {
            'date': '19.05.2024 09:00:00',
            'category': 'Разное',
            'amount': 1000.0
        }
    ]


def test_analyze_cashback_categories_success(sample_transactions):
    result = analyze_cashback_categories(sample_transactions, 2024, 5)

    assert 'Супермаркеты' in result
    assert 'Кафе' in result
    assert 'Транспорт' in result
    assert result['Супермаркеты'] == 80.0
    assert result['Кафе'] == 15.0
    assert result['Транспорт'] == 20.0


def test_analyze_cashback_categories_wrong_date(sample_transactions):
    result = analyze_cashback_categories(sample_transactions, 2024, 6)
    assert result == {}


def test_analyze_cashback_categories_empty_data():
    result = analyze_cashback_categories([], 2024, 5)
    assert result == {}


def test_analyze_cashback_categories_only_income():
    income_transactions = [
        {
            'date': '15.05.2024 12:00:00',
            'category': 'Зарплата',
            'amount': 50000.0
        }
    ]

    result = analyze_cashback_categories(income_transactions, 2024, 5)
    assert result == {}


@pytest.mark.parametrize("year,month,expected_categories", [
    (2024, 5, ['Супермаркеты', 'Кафе', 'Транспорт']),
    (2023, 5, []),
    (2024, 4, [])
])
def test_analyze_cashback_categories_parameterized(sample_transactions, year, month, expected_categories):
    result = analyze_cashback_categories(sample_transactions, year, month)

    if expected_categories:
        for category in expected_categories:
            assert category in result
    else:
        assert result == {}


def test_get_cashback_analysis_json_format(sample_transactions):
    result_json = get_cashback_analysis(sample_transactions, 2024, 5)
    result_dict = json.loads(result_json)

    assert isinstance(result_dict, dict)
    assert 'Супермаркеты' in result_dict
    assert result_dict['Супермаркеты'] == 80.0


def test_analyze_cashback_categories_sorting(sample_transactions):
    result = analyze_cashback_categories(sample_transactions, 2024, 5)

    categories = list(result.keys())
    values = list(result.values())

    assert values == sorted(values, reverse=True)
    assert categories[0] == 'Супермаркеты'
