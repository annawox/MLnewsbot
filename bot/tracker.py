import os
import requests
import time
import logging

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    filename="bot.log"  # Логи будут сохраняться в файл bot.log
)

# Настройки
REPOSITORIES_FILE = os.path.join(os.path.dirname(__file__), "repositories.txt")  # Путь к файлу
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")  # Токен из Secrets
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")  # Chat ID из Secrets

# Функция для чтения репозиториев из файла
def load_repositories():
    try:
        with open(REPOSITORIES_FILE, "r") as file:
            return [line.strip() for line in file if line.strip()]
    except FileNotFoundError:
        logging.error(f"Файл {REPOSITORIES_FILE} не найден")
        return []

# Функция для отправки сообщения в Telegram
def send_telegram_message(message):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message,
            "parse_mode": "Markdown"  # Включаем поддержку Markdown
        }
        response = requests.post(url, json=payload)
        response.raise_for_status()  # Проверка на ошибки HTTP
        logging.info(f"Сообщение отправлено: {message}")
    except requests.exceptions.RequestException as e:
        logging.error(f"Ошибка при отправке сообщения в Telegram: {e}")

# Функция для проверки релизов
def check_github_releases(repo):
    try:
        url = f"https://api.github.com/repos/{repo}/releases"
        response = requests.get(url)
        response.raise_for_status()  # Проверка на ошибки HTTP
        releases = response.json()
        if releases:
            return (
                releases[0]["id"],  # ID релиза
                releases[0]["name"],  # Название релиза
                releases[0]["html_url"],  # Ссылка на релиз
                releases[0]["body"]  # Описание релиза
            )
    except requests.exceptions.RequestException as e:
        logging.error(f"Ошибка при запросе к GitHub API: {e}")
    return None, None, None, None

# Загружаем репозитории
REPOSITORIES = load_repositories()

# Словарь для хранения последних отправленных релизов
last_sent_releases = {repo: None for repo in REPOSITORIES}

# Основной цикл
logging.info("Скрипт запущен")
try:
    while True:
        for repo in REPOSITORIES:
            latest_release_id, latest_release_name, latest_release_url, latest_release_body = check_github_releases(repo)
            if latest_release_id and latest_release_id != last_sent_releases[repo]:
                # Формируем сообщение
                repo_name = repo.split("/")[-1]  # Получаем имя репозитория (например, "transformers")
                message = (
                    f"новый релиз {repo_name}: {latest_release_name}\n"
                    f"[подробнее]({latest_release_url})\n\n"
                    f"Описание:\n{latest_release_body[:400]}..."  # Обрезаем описание до 400 символов
                )
                send_telegram_message(message)
                last_sent_releases[repo] = latest_release_id  # Обновляем последний отправленный релиз
        time.sleep(3600)  # Проверка каждый час
except KeyboardInterrupt:
    logging.info("Скрипт завершен")
except Exception as e:
    logging.error(f"Неожиданная ошибка: {e}")
