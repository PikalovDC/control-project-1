from unittest.mock import Mock, patch

import pytest

from src.external_api import get_currency_rates, get_stock_prices


@pytest.fixture
def sample_currencies():
    return ["USD", "EUR", "RUB"]


@pytest.fixture
def sample_stocks():
    return ["AAPL", "GOOGL", "TSLA"]


@pytest.fixture
def mock_currency_response():
    return {
        "success": True,
        "result": 75.50
    }


@pytest.fixture
def mock_stock_response():
    return {
        "data": [
            {
                "close": 150.25
            }
        ]
    }


# Тесты для get_currency_rates
@patch('src.external_api.requests.get')
@patch('src.external_api.os.getenv')
def test_get_currency_rates_success(mock_getenv, mock_requests_get, sample_currencies, mock_currency_response):
    """Тест успешного получения курсов валют"""
    # Мокируем API ключ
    mock_getenv.return_value = "test_api_key"

    # Мокируем успешный ответ API
    mock_response = Mock()
    mock_response.json.return_value = mock_currency_response
    mock_response.raise_for_status.return_value = None
    mock_requests_get.return_value = mock_response

    result = get_currency_rates(sample_currencies)

    assert "currency_rates" in result
    assert len(result["currency_rates"]) == 3

    # Проверяем структуру ответа
    currencies = [rate["currency"] for rate in result["currency_rates"]]
    assert "USD" in currencies
    assert "EUR" in currencies
    assert "RUB" in currencies

    # RUB должен иметь курс 1.0
    rub_rate = next(rate for rate in result["currency_rates"] if rate["currency"] == "RUB")
    assert rub_rate["rate"] == 1.0


@patch('src.external_api.os.getenv')
def test_get_currency_rates_no_api_key(mock_getenv, sample_currencies):
    """Тест отсутствия API ключа"""
    mock_getenv.return_value = None

    result = get_currency_rates(sample_currencies)

    assert result == {"currency_rates": []}


@patch('src.external_api.requests.get')
@patch('src.external_api.os.getenv')
def test_get_currency_rates_api_error(mock_getenv, mock_requests_get, sample_currencies):
    """Тест ошибки API"""
    mock_getenv.return_value = "test_api_key"
    mock_requests_get.side_effect = Exception("API error")

    result = get_currency_rates(["USD"])

    assert result == {"currency_rates": []}


@patch('src.external_api.requests.get')
@patch('src.external_api.os.getenv')
def test_get_currency_rates_failed_response(mock_getenv, mock_requests_get, sample_currencies):
    """Тест неудачного ответа API"""
    mock_getenv.return_value = "test_api_key"

    mock_response = Mock()
    mock_response.json.return_value = {"success": False}
    mock_response.raise_for_status.return_value = None
    mock_requests_get.return_value = mock_response

    result = get_currency_rates(["USD"])

    assert result == {"currency_rates": []}


# Параметризованные тесты для разных валют
@pytest.mark.parametrize("currency,expected_in_result", [
    ("USD", True),
    ("EUR", True),
    ("GBP", True),
    ("JPY", True),
])
@patch('src.external_api.requests.get')
@patch('src.external_api.os.getenv')
def test_get_currency_rates_different_currencies(mock_getenv, mock_requests_get, currency, expected_in_result,
                                                 mock_currency_response):
    """Тест для разных валют"""
    mock_getenv.return_value = "test_api_key"

    mock_response = Mock()
    mock_response.json.return_value = mock_currency_response
    mock_response.raise_for_status.return_value = None
    mock_requests_get.return_value = mock_response

    result = get_currency_rates([currency])

    if expected_in_result:
        assert len(result["currency_rates"]) == 1
        assert result["currency_rates"][0]["currency"] == currency
    else:
        assert result["currency_rates"] == []


# Тесты для get_stock_prices
@patch('src.external_api.requests.get')
@patch('src.external_api.os.getenv')
def test_get_stock_prices_success(mock_getenv, mock_requests_get, sample_stocks, mock_stock_response):
    """Тест успешного получения цен акций"""
    mock_getenv.return_value = "test_api_key"

    mock_response = Mock()
    mock_response.json.return_value = mock_stock_response
    mock_response.raise_for_status.return_value = None
    mock_requests_get.return_value = mock_response

    result = get_stock_prices(sample_stocks)

    assert "stock_prices" in result
    assert len(result["stock_prices"]) == 3

    stocks = [stock["stock"] for stock in result["stock_prices"]]
    assert "AAPL" in stocks
    assert "GOOGL" in stocks
    assert "TSLA" in stocks


@patch('src.external_api.os.getenv')
def test_get_stock_prices_no_api_key(mock_getenv, sample_stocks):
    """Тест отсутствия API ключа для акций"""
    mock_getenv.return_value = None

    result = get_stock_prices(sample_stocks)

    assert result == {"stock_prices": []}


# Параметризованные тесты для разных акций
@pytest.mark.parametrize("stock_symbol", [
    "AAPL",
    "GOOGL",
    "MSFT",
    "TSLA",
    "AMZN",
])
@patch('src.external_api.requests.get')
@patch('src.external_api.os.getenv')
def test_get_stock_prices_different_stocks(mock_getenv, mock_requests_get, stock_symbol, mock_stock_response):
    """Тест для разных акций"""
    mock_getenv.return_value = "test_api_key"

    mock_response = Mock()
    mock_response.json.return_value = mock_stock_response
    mock_response.raise_for_status.return_value = None
    mock_requests_get.return_value = mock_response

    result = get_stock_prices([stock_symbol])

    assert len(result["stock_prices"]) == 1
    assert result["stock_prices"][0]["stock"] == stock_symbol
    assert isinstance(result["stock_prices"][0]["price"], float)
