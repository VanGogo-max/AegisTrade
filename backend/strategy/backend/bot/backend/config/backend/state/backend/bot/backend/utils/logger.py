import logging
import os


class Logger:
    """
    Централизиран логер за бота
    """

    def __init__(self, name: str = "trading_bot", log_file: str = "backend/logs/bot.log"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)

        # избягваме дублиране на handlers
        if not self.logger.handlers:

            # създаване на папка ако липсва
            os.makedirs(os.path.dirname(log_file), exist_ok=True)

            # file handler
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(logging.INFO)

            # console handler
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)

            # формат
            formatter = logging.Formatter(
                "%(asctime)s | %(levelname)s | %(message)s"
            )

            file_handler.setFormatter(formatter)
            console_handler.setFormatter(formatter)

            self.logger.addHandler(file_handler)
            self.logger.addHandler(console_handler)

    # ---------------- METHODS ----------------

    def info(self, message: str):
        self.logger.info(message)

    def warning(self, message: str):
        self.logger.warning(message)

    def error(self, message: str):
        self.logger.error(message)

    def debug(self, message: str):
        self.logger.debug(message)
