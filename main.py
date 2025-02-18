import telebot
import logging
import time
from rich.console import Console
from FunPayAPI import Account

# Инициализация Rich для красивого вывода
console = Console()

# Настройка Telegram-бота
TELEGRAM_BOT_TOKEN = "7615831385:AAFLrD-FGGJQQlocF8SUyrBLqcLayznGolM"  # Замените на ваш токен бота

# Создаем экземпляр Telegram-бота
telegram_bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

# Логирование в Telegram
def send_to_telegram(message):
    try:
        # Отправляем сообщение всем пользователям
        for user_id in get_all_users():
            telegram_bot.send_message(user_id, message)
    except Exception as e:
        console.print(f"[red]Ошибка отправки сообщения в Telegram: {e}[/red]")

# Получение всех пользователей (подписчиков бота)
def get_all_users():
    # Здесь можно реализовать логику получения всех пользователей из базы данных или файла
    # В данном примере просто возвращаем список ID пользователей
    return [5777052726]  # Замените на реальные ID пользователей

# Переопределение стандартного логгера
class TelegramLogger(logging.Handler):
    def emit(self, record):
        log_entry = self.format(record)
        console.print(log_entry)  # Вывод в терминал
        send_to_telegram(log_entry)  # Отправка в Telegram

# Настройка логгера
logger = logging.getLogger("FPV")
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%H:%M:%S')
handler = TelegramLogger()
handler.setFormatter(formatter)
logger.addHandler(handler)

class Vertex:
    def __init__(self, golden_key: str, user_agent: str):
        self.account = Account(golden_key, user_agent)
        self.raise_time = {}
        self.profile = None

    def init_account(self):
        """Инициализация аккаунта."""
        with console.status("[bold green]Инициализация аккаунта...[/bold green]", spinner="dots"):
            while True:
                try:
                    self.account.get()
                    self.profile = self.account.get_user(self.account.id)
                    logger.info("Аккаунт успешно инициализирован.")
                    break
                except Exception as e:
                    logger.error(f"Ошибка инициализации аккаунта: {e}")
                    time.sleep(2)

    def raise_lots(self):
        """Поднятие лотов."""
        next_call = float("inf")
        categories = self.profile.get_sorted_lots(2)

        for subcat in categories:
            if self.raise_time.get(subcat.category.id, 0) > time.time():
                next_call = min(next_call, self.raise_time[subcat.category.id])
                continue

            try:
                time.sleep(0.5)
                self.account.raise_lots(subcat.category.id)
                logger.info(f"Лоты категории {subcat.category.name} успешно подняты")
                next_time = time.time() + 10800  # 3 часа
            except Exception as e:
                wait_time = getattr(e, 'wait_time', 10)
                logger.warning(f"Ошибка при поднятии лотов категории {subcat.category.name}: {e}")
                next_time = time.time() + wait_time

            self.raise_time[subcat.category.id] = next_time
            next_call = min(next_call, next_time)

        return next_call if next_call < float("inf") else 10

    def lots_raise_loop(self):
        """Бесконечный цикл поднятия лотов."""
        self.init_account()
        logger.info("Запущен цикл поднятия лотов")

        while True:
            try:
                next_time = self.raise_lots()
                delay = max(next_time - time.time(), 0)

                # Уведомления о времени до поднятия
                if delay > 3600:
                    logger.info(f"Следующее поднятие лотов через {int(delay / 3600)} часов.")
                elif delay > 300:
                    logger.info(f"Следующее поднятие лотов через {int(delay / 60)} минут.")
                elif delay > 60:
                    for i in range(int(delay), 0, -60):
                        logger.info(f"Поднятие лотов через {i // 60} минут.")
                        time.sleep(60)
                else:
                    for i in range(int(delay), 0, -1):
                        logger.info(f"Поднятие лотов через {i} секунд.")
                        time.sleep(1)

                time.sleep(delay)
            except Exception as e:
                logger.error(f"Критическая ошибка: {e}")
                time.sleep(10)

def main():
    # Инициализация бота
    vertex = Vertex(
        golden_key="7cmaq8xoy9ui8tte3otvwdmtgfcozka6",
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36"
    )
    vertex.lots_raise_loop()

if __name__ == "__main__":
    main()
