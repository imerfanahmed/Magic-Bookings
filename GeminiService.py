import google.generativeai as genai
from Config import Config
import requests

class GeminiService:
    def __init__(self):
        print(Config.GEMINI_API_KEY)
        genai.configure(api_key=Config.GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        self.conversations = {}  # Stores conversation history by user ID

    def _initialize_conversation(self, user_id: str):
        if user_id not in self.conversations:
            self.conversations[user_id] = self.model.start_chat(history=[])
            self.conversations[user_id].send_message(Config.SYSTEM_PROMPT)

    def process_message(self, user_id: str, message: str) -> str:
        self._initialize_conversation(user_id)
        
        try:
            response = self.conversations[user_id].send_message(message)
            response_text = response.text

            # Check if the response confirms a booking
            if "booking confirmed" in response_text.lower():
                booking_info = self.extract_booking_info(user_id, response_text)
                self.send_booking_confirmation(booking_info)
            
            return response_text
        except Exception as e:
            return "Sorry, I'm having trouble processing your request. Please try again later."

    def extract_booking_info(self, user_id: str, response_text: str) -> dict:
        # Extract booking information from the response text
        # This is a placeholder implementation and should be replaced with actual extraction logic
        return {
            "user_id": user_id,
            "booking_details": response_text
        }

    def send_booking_confirmation(self, booking_info: dict):
        url = "https://example.com/api/bookings"
        headers = {"Content-Type": "application/json"}
        try:
            response = requests.post(url, json=booking_info, headers=headers)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"Failed to send booking confirmation: {e}")

    def end_conversation(self, user_id: str):
        if user_id in self.conversations:
            del self.conversations[user_id]