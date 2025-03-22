import os
import requests
import time

# Настройки
REPOSITORIES = [
    "openai/gpt-4",  # Репозиторий OpenAI
    "google-research/bert",  # Репозиторий Google Research
    "huggingface/transformers"  # Репозиторий Hugging Face
]
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")  # Токен из Secrets
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")  # Chat ID из Secrets

# Функция для отправки сообщения в Telegram
def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message
    }
    requests.post(url, json=payload)

# Функция для проверки релизов
def check_github_releases(repo):
    url = f"https://api.github.com/repos/{repo}/releases"
    response = requests.get(url)
    if response.status_code == 200:
        releases = response.json()
        if releases:
            return releases[0]["name"]  # Имя последнего релиза
    return None

# Словарь для хранения последних релизов
last_releases = {repo: None for repo in REPOSITORIES}

# Основной цикл
while True:
    for repo in REPOSITORIES:
        latest_release = check_github_releases(repo)
        if latest_release and latest_release != last_releases[repo]:
            message = f"Новый релиз в {repo}: {latest_release}"
            send_telegram_message(message)
            last_releases[repo] = latest_release
    time.sleep(3600)  # Проверка каждый час
