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

    def handle_verification(self, request_args: Dict[str, str]) -> tuple:
        mode = request_args.get("hub.mode")
        token = request_args.get("hub.verify_token")
        challenge = request_args.get("hub.challenge")

        if mode == "subscribe" and token == "magicoffice":
            return challenge, 200
        return "Verification failed", 403

    def handle_incoming_message(self, payload: Dict[str, Any]) -> tuple:
        self.logger.debug(f"Incoming message data: {payload}")

        if "entry" not in payload:
            return jsonify({"status": "invalid request"}), 400

        for entry in payload["entry"]:
            for change in entry.get("changes", []):
                if change.get("field") == "messages":
                    self._process_message_change(change.get("value", {}))

        return jsonify({"status": "success"}), 200

    def _process_message_change(self, message_data: Dict[str, Any]):
        if not message_data.get("messages"):
            return
            
        message = message_data.get("messages", [{}])[0]
        sender = message.get("from")

        if not sender:
            return

        # Handle different message types
        if "image" in message:
            self._handle_image_message(sender, message)
        elif "text" in message:
            user_input = message.get("text", {}).get("body", "").strip()
            if user_input.lower() in ["exit", "quit", "bye", "goodbye"]:
                self._handle_exit_command(sender)
            else:
                self._handle_text_message(sender, user_input)
        else:
            # Handle other message types
            self.meta_client.send_message(
                sender, 
                "I can only analyze chest X-ray images. Please send an image file (JPEG or PNG) for radiological analysis."
            )

    def _handle_image_message(self, sender: str, message: Dict[str, Any]):
        """Handle incoming image messages for X-ray analysis"""
        try:
            image_info = message.get("image", {})
            image_id = image_info.get("id")
            mime_type = image_info.get("mime_type", "image/jpeg")
            caption = image_info.get("caption", "")

            if not image_id:
                self.meta_client.send_message(sender, "❌ Unable to process the image. Please try uploading again.")
                return

            # Download image from Meta servers
            image_url = self._get_media_url(image_id)
            if not image_url:
                self.meta_client.send_message(sender, "❌ Unable to retrieve the image. Please try again.")
                return

            # Download image data
            image_data = self.gemini_service.download_image(image_url, self.meta_client.access_token)
            if not image_data:
                self.meta_client.send_message(sender, "❌ Failed to download the image. Please try again.")
                return

            # Validate image type
            if not mime_type.startswith("image/"):
                self.meta_client.send_message(
                    sender, 
                    "❌ Please send a valid image file (JPEG or PNG format) of a chest X-ray."
                )
                return

            # Send processing message
            self.meta_client.send_message(sender, "🔍 Analyzing your chest X-ray image... Please wait.")

            # Process image with Gemini
            response_text = self.gemini_service.process_image(sender, image_data, mime_type, caption)
            
            # Send analysis result
            self.meta_client.send_message(sender, response_text)

        except Exception as e:
            self.logger.error(f"Error handling image: {str(e)}")
            self.meta_client.send_message(
                sender, 
                "❌ An error occurred while processing your image. Please try again or contact support."
            )

    def _handle_text_message(self, sender: str, message: str):
        """Handle text messages"""
        response_text = self.gemini_service.process_message(sender, message)
        self.meta_client.send_message(sender, response_text)

    def _handle_exit_command(self, sender: str):
        """Handle exit/goodbye commands"""
        self.gemini_service.end_conversation(sender)
        goodbye_message = """👋 **Thank you for using AI Radiology Assistant**

Remember: This analysis is for educational purposes only. For urgent medical concerns, please contact your healthcare provider immediately.

Feel free to return anytime with new chest X-ray images for analysis."""
        
        self.meta_client.send_message(sender, goodbye_message)

    def _get_media_url(self, media_id: str) -> Optional[str]:
        """Get media URL from Meta Graph API"""
        try:
            url = f"https://graph.facebook.com/v18.0/{media_id}"
            headers = {"Authorization": f"Bearer {self.meta_client.access_token}"}
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            return response.json().get("url")
        except Exception as e:
            self.logger.error(f"Failed to get media URL: {str(e)}")
            return None