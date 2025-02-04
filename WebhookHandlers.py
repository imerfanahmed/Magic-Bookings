from flask import request, jsonify
from typing import Dict, Any, Optional
import logging
import requests
from MetaClient import MetaClient
from GeminiService import GeminiService

class WebhookHandler:
    def __init__(self):
        self.meta_client = MetaClient()
        self.gemini_service = GeminiService()
        self.logger = logging.getLogger(__name__)
        self.user_states = {}  # Track user conversation states

    def handle_verification(self, request_args: Dict[str, str]) -> tuple:
        # Existing verification logic remains unchanged
        mode = request_args.get("hub.mode")
        token = request_args.get("hub.verify_token")
        challenge = request_args.get("hub.challenge")

        if mode == "subscribe" and token == "magicoffice":
            return challenge, 200
        return "Verification failed", 403

    def handle_incoming_message(self, payload: Dict[str, Any]) -> tuple:
        # Existing payload handling remains unchanged
        self.logger.debug(f"Incoming message data: {payload}")

        if "entry" not in payload:
            return jsonify({"status": "invalid request"}), 400

        for entry in payload["entry"]:
            for change in entry.get("changes", []):
                if change.get("field") == "messages":
                    self._process_message_change(change.get("value", {}))

        return jsonify({"status": "success"}), 200

    def _process_message_change(self, message_data: Dict[str, Any]):
        # Existing message processing remains unchanged
        message = message_data.get("messages", [{}])[0]
        sender = message.get("from")
        user_input = message.get("text", {}).get("body", "").strip().lower()

        if not sender or not user_input:
            return

        if user_input in ["exit", "quit"]:
            self._handle_exit_command(sender)
        else:
            self._handle_normal_message(sender, user_input)

    def _handle_exit_command(self, sender: str):
        # Existing exit handling remains unchanged
        self.gemini_service.end_conversation(sender)
        self.user_states.pop(sender, None)  # Clear state on exit
        self.meta_client.send_message(sender, "Goodbye! We hope to see you soon! 🍽️")

    def _handle_normal_message(self, sender: str, message: str):
        # Get current user state
        current_state = self.user_states.get(sender, "normal")

        if current_state == "awaiting_confirmation":
            # Handle confirmation response
            if message in ["yes", "confirm"]:
                success = self._submit_confirmation(sender)
                response_text = "✅ Reservation confirmed!" if success else "❌ Confirmation failed"
            else:
                response_text = "❌ Reservation cancelled"
            
            # Reset user state
            self.user_states.pop(sender, None)
        else:
            # Process normal message
            response_text = self.gemini_service.process_message(sender, message)
            
            # Check if we should enter confirmation state
            if self._is_confirmation_prompt(response_text):
                self.user_states[sender] = "awaiting_confirmation"

        self.meta_client.send_message(sender, response_text)

    def _is_confirmation_prompt(self, response_text: str) -> bool:
        """Determine if the response is asking for confirmation"""
        return any(keyword in response_text.lower() 
                  for keyword in ["confirm", "proceed", "continue"])

    def _submit_confirmation(self, sender: str) -> bool:
        """Submit POST request to external API"""
        try:
            # Customize your payload and endpoint here
            response = requests.post(
                "https://api.your-service.com/confirm",
                json={
                    "user_id": sender,
                    "action": "reservation_confirmation"
                },
                timeout=5
            )
            return response.status_code == 200
        except Exception as e:
            self.logger.error(f"Confirmation POST failed: {str(e)}")
            return False