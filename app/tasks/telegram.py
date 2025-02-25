import logging
import requests
from typing import Optional
from app.core.config import settings

logger = logging.getLogger(__name__)

class TelegramNotifier:
    def __init__(self):
        self.token = settings.TELEGRAM_TOKEN
        self.chat_id = settings.TELEGRAM_CHAT_ID
        self.base_url = f"https://api.telegram.org/bot{self.token}"
        
    def send_message(self, text: str) -> bool:
        """Отправляет сообщение в Telegram чат"""
        try:
            response = requests.post(
                f"{self.base_url}/sendMessage",
                json={
                    "chat_id": self.chat_id,
                    "text": text,
                    "parse_mode": "Markdown"
                },
                timeout=10
            )
            response.raise_for_status()
            return True
        except Exception as e:
            logger.error(f"Telegram send error: {str(e)}")
            return False

    def format_welcome_message(self, email: str) -> str:
        """Форматирует приветственное сообщение"""
        return f"""
        🎉 *Новый пользователь* 🎉
        Email: `{email}`
        """

telegram = TelegramNotifier()