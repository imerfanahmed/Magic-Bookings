from flask import Flask, request
import logging
from WebhookHandlers import WebhookHandler
import os

def create_app():
    app = Flask(__name__)
    handler = WebhookHandler()
    
    @app.route("/webhook", methods=["GET"])
    def verify_webhook():
        return handler.handle_verification(request.args)

    @app.route("/webhook", methods=["POST"])
    def handle_webhook():
        return handler.handle_incoming_message(request.json)

    @app.route("/health", methods=["GET"])
    def health_check():
        return {"status": "healthy", "service": "AI Radiology Assistant"}, 200

    return app

if __name__ == "__main__":
    # Verify environment variables are set
    if not os.getenv("GEMINI_API_KEY"):
        print("ERROR: GEMINI_API_KEY environment variable is not set")
        exit(1)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    logger = logging.getLogger(__name__)
    logger.info("Starting AI Radiology Assistant service...")
    
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)