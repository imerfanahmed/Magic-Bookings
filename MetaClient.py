import requests
import logging
from Config import Config

class MetaClient:
    def __init__(self):
        self.api_url = Config.META_API_URL
        self.access_token = Config.META_ACCESS_TOKEN
        self.logger = logging.getLogger(__name__)

    def send_message(self, to: str, message: str) -> bool:
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }
        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "text",
            "text": {"body": message},
        }
        
        try:
            response = requests.post(self.api_url, headers=headers, json=payload)
            response.raise_for_status()
            self.logger.debug(f"Message sent to {to}: {message}")
            return True
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to send message: {str(e)}")
            return False