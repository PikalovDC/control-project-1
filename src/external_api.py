import logging
import os
from typing import Any, Dict

import requests
from dotenv import load_dotenv

load_dotenv()

# Создаем логгер для этого модуля
logger = logging.getLogger('external_api')


def get_currency_rates(currencies: list) -> Dict[str, Any]:
    """
    Получает курсы валют из API для списка валют.
    """
    api_key = os.getenv('API_KEY')
    if not api_key:
        logger.error("API_KEY not found in environment variables")
        return {"currency_rates": []}

    result = {"currency_rates": []}

    for currency in currencies:
        try:
            if currency == "RUB":
                rate = 1.0
            else:
                url = "https://api.apilayer.com/exchangerates_data/convert"
                headers = {"apikey": api_key}
                params = {
                    "from": currency,
                    "to": "RUB",
                    "amount": 1
                }

                response = requests.get(url, headers=headers, params=params, timeout=10)
                response.raise_for_status()

                data = response.json()

                if data.get("success", False):
                    rate = data["result"]
                else:
                    raise ValueError(f"API error for {currency}")

            result["currency_rates"].append({
                "currency": currency,
                "rate": round(rate, 2)
            })

            logger.info(f"Успешно получен курс для {currency}: {rate}")

        except Exception as e:
            logger.error(f"Ошибка получения курса {currency}: {e}")
            continue

    return result


def get_stock_prices(stocks: list) -> Dict[str, Any]:
    """
    Получает цены акций из API для списка акций.
    """
    api_key = os.getenv('MARKETSTACK_API_KEY')
    if not api_key:
        logger.error("MARKETSTACK_API_KEY not found in environment variables")
        return {"stock_prices": []}

    result = {"stock_prices": []}

    for stock in stocks:
        try:
            url = "http://api.marketstack.com/v1/eod/latest"
            params = {
                "access_key": api_key,
                "symbols": stock
            }

            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()

            if 'data' in data and len(data['data']) > 0:
                price = float(data['data'][0]['close'])

                result["stock_prices"].append({
                    "stock": stock,
                    "price": round(price, 2)
                })

                logger.info(f"Успешно получена цена для {stock}: {price}")
            else:
                raise ValueError(f"Price not found for {stock}")

        except Exception as e:
            logger.error(f"Ошибка получения цены {stock}: {e}")
            continue

    return result
