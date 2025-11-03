import logging
from pathlib import Path


def setup_logging():
    """Настройка логирования для всего проекта"""

    # Создаем папку logs в корне проекта
    log_dir = Path("..") / "logs"  # ../logs из папки src
    log_dir.mkdir(exist_ok=True)

    # Формат логов
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Конфигурация логгера для модуля utils
    utils_logger = logging.getLogger('utils')
    utils_logger.setLevel(logging.DEBUG)
    utils_logger.handlers = []
    utils_file_handler = logging.FileHandler('../logs/utils.log', mode='w', encoding='utf-8')
    utils_file_handler.setFormatter(formatter)
    utils_logger.addHandler(utils_file_handler)

    # Конфигурация логгера для модуля external_api
    api_logger = logging.getLogger('external_api')
    api_logger.setLevel(logging.DEBUG)
    api_logger.handlers = []
    api_file_handler = logging.FileHandler('../logs/api.log', mode='w', encoding='utf-8')
    api_file_handler.setFormatter(formatter)
    api_logger.addHandler(api_file_handler)

    # Конфигурация логгера для модуля views
    views_logger = logging.getLogger('views')
    views_logger.setLevel(logging.DEBUG)
    views_logger.handlers = []
    views_file_handler = logging.FileHandler('../logs/views.log', mode='w', encoding='utf-8')
    views_file_handler.setFormatter(formatter)
    views_logger.addHandler(views_file_handler)

    # Конфигурация логгера для модуля services
    services_logger = logging.getLogger('services')
    services_logger.setLevel(logging.DEBUG)
    services_logger.handlers = []
    services_file_handler = logging.FileHandler('../logs/services.log', mode='w', encoding='utf-8')
    services_file_handler.setFormatter(formatter)
    services_logger.addHandler(services_file_handler)

    # Конфигурация логгера для модуля reports
    reports_logger = logging.getLogger('reports')
    reports_logger.setLevel(logging.DEBUG)
    reports_logger.handlers = []
    reports_file_handler = logging.FileHandler('../logs/reports.log', mode='w', encoding='utf-8')
    reports_file_handler.setFormatter(formatter)
    reports_logger.addHandler(reports_file_handler)
