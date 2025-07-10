import google.generativeai as genai
from Config import Config
import requests
import base64
from typing import Optional, Dict, Any
import logging

class GeminiService:
    def __init__(self):
        genai.configure(api_key=Config.GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-2.5-pro')
        self.conversations = {}  # Stores conversation history by user ID
        self.logger = logging.getLogger(__name__)

    def _initialize_conversation(self, user_id: str):
        if user_id not in self.conversations:
            self.conversations[user_id] = self.model.start_chat(history=[])
            # Send initial greeting without the full system prompt
            greeting = """Hello! I'm your AI Radiology Assistant specializing in chest X-ray analysis. 

Please upload a clear chest X-ray image (JPEG or PNG format) and I'll provide you with a detailed radiological report.

**Supported views:** PA (Posterior-Anterior), AP (Anterior-Posterior), Lateral

**Image quality requirements:**
- Adequate penetration
- Proper positioning  
- Full inspiration
- No motion artifacts

Please send your chest X-ray image to begin the analysis."""
            
            return greeting

    def process_message(self, user_id: str, message: str) -> str:
        # Check if this is a new conversation
        if user_id not in self.conversations:
            greeting = self._initialize_conversation(user_id)
            return greeting
        
        try:
            # For text messages, guide user to upload image
            response = self.conversations[user_id].send_message(
                f"System context: {Config.SYSTEM_PROMPT}\n\nUser message: {message}"
            )
            return response.text
        except Exception as e:
            self.logger.error(f"Error processing message: {str(e)}")
            return "Sorry, I'm having trouble processing your request. Please try again or upload a chest X-ray image for analysis."

    def process_image(self, user_id: str, image_data: bytes, mime_type: str, caption: Optional[str] = None) -> str:
        """Process chest X-ray image and return radiological analysis"""
        self._initialize_conversation(user_id)
        
        try:
            # Create image object for Gemini
            image_parts = [{
                "mime_type": mime_type,
                "data": image_data
            }]
            
            # Prepare the prompt for image analysis
            analysis_prompt = f"""
            {Config.SYSTEM_PROMPT}
            
            Please analyze this chest X-ray image and provide a detailed structured radiological report following the format specified above.
            
            User caption: {caption if caption else "No additional clinical information provided"}
            """
            
            # Send image and prompt to Gemini
            response = self.conversations[user_id].send_message([analysis_prompt] + image_parts)
            
            return response.text
            
        except Exception as e:
            self.logger.error(f"Error processing image: {str(e)}")
            return """❌ **Image Analysis Error**
            
I encountered an error while analyzing the image. Please ensure:
- The image is a chest X-ray in JPEG or PNG format
- The image file is not corrupted
- The image is clear and properly positioned

Please try uploading the image again. For technical support, please contact our support team."""

    def download_image(self, image_url: str, access_token: str) -> Optional[bytes]:
        """Download image from WhatsApp/Meta servers"""
        try:
            headers = {"Authorization": f"Bearer {access_token}"}
            response = requests.get(image_url, headers=headers, timeout=30)
            response.raise_for_status()
            return response.content
        except Exception as e:
            self.logger.error(f"Failed to download image: {str(e)}")
            return None

    def end_conversation(self, user_id: str):
        if user_id in self.conversations:
            del self.conversations[user_id]