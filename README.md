# Банковские операции
Приложение для анализа транзакций, которые находятся в Excel-файле. Приложение будет генерировать JSON-данные для
веб - страниц

## Содержание


## Установка
git clone https://github.com/PikalovDC/control-project-1.git

## Требования
* Python 3.7+
* Стандартные библиотеки Python

## Функционал

# Документация функций

## Модуль `src/views.py`

### `get_main_page_data(date_string: str) -> Dict[str, Any]`
Главная функция API, генерирует полный JSON-ответ для веб-страницы.

## Модуль `src/utils.py` Вспомогательные функции

### `get_greeting(date_string: str) -> str`
Определяет приветствие по времени суток.

#### Пример использования:

from src.utils import get_greeting
greeting = get_greeting("2024-05-15 08:00:00")

### `get_month_range(date_string: str) -> tuple[str, str]`
Вычисляет диапазон дат с 1 числа месяца по указанную дату.

#### Пример использования:

from src.utils import get_month_range
start_date, end_date = get_month_range("2024-05-15 14:30:00")

### `load_excel_transactions(start_date: str, end_date: str) -> List[Dict[str, Any]]`
Загружает транзакции из Excel файла и фильтрует по дате и статусу.

#### Пример использования:

from src.utils import load_excel_transactions
transactions = load_excel_transactions("2024-05-01", "2024-05-15")

### `is_valid_transaction(transaction: Dict[str, Any], start_date: str, end_date: str) -> bool`
Проверяет валидность транзакции.

### `standardize_transaction(transaction: Dict[str, Any]) -> Dict[str, Any]`
Приводит транзакцию к единому формату.

### `get_cards_data(transactions: List[Dict[str, Any]]) -> List[Dict[str, Any]]`
Рассчитывает данные по банковским картам.

### `get_top_transactions(transactions: List[Dict[str, Any]], limit: int = 5) -> List[Dict[str, Any]]`
Возвращает топ-N транзакций по сумме расходов.

## Модуль `src/external_api.py`

### `get_currency_rates(currencies: list) -> Dict[str, Any]`
Получает актуальные курсы валют из API.

### `get_stock_prices(stocks: list) -> Dict[str, Any]`
Получает актуальные цены акций из API.

## Модуль services.py - Документация

## Описание
Модуль `services.py` содержит сервисные функции для аналитики финансовых данных, реализованные с элементами функционального программирования.

## Функции

### `analyze_cashback_categories(data: List[Dict[str, Any]], year: int, month: int) -> Dict[str, float]`
Анализирует выгодность категорий для повышенного кешбэка.

**Параметры:**
- `data` (List[Dict]): Список транзакций
- `year` (int): Год для анализа  
- `month` (int): Месяц для анализа

**Возвращает:**
- `Dict[str, float]`: Словарь с категориями и суммами кешбэка, отсортированный по убыванию

### `get_cashback_analysis(data: List[Dict[str, Any]], year: int, month: int) -> str`
Возвращает анализ кешбэка в формате JSON.


## Модуль `src/logging_config.py`

### `setup_logging() -> None`
Настраивает систему логирования для всего проекта.

# Разработка
Проект находится в активной разработке.

# Тестирование
## Установка Pytest
Если Pytest еще не установлен, установите его с помощью poetry:
`poetry add --group dev pytest`

Запустите тесты используя команду `pytest`

## Структура тестов
Тесты организованы в соответствии со структурой проекта - находятся в папке 'tests'.

Каждый тестовый файл соответствует отдельному модулю и содержит:
+ Фикстуры (fixtures) для подготовки тестовых данных

+ Тестовые функции с префиксом test_

+ Параметризованные тесты для проверки различных сценариев

+ Тесты обработки ошибок с использованием pytest.raises

## Покрытие тестами
В pytest для анализа покрытия кода надо поставить библиотеку 
pytest-cov:

`# Через poetry с добавлением в отдельную группу
poetry add --group dev pytest-cov`

Чтобы запустить тесты с оценкой покрытия, можно воспользоваться следующими командами:

+ `pytest --cov` — при активированном виртуальном окружении.
+ `poetry run pytest --cov` — через poetry.
+ `pytest --cov=src --cov-report=html` — чтобы сгенерировать отчет о покрытии в HTML-формате, где 
src — пакет c модулями, которые тестируем. Отчет будет сгенерирован в папке 
htmlcov и храниться в файле с названием index.html
