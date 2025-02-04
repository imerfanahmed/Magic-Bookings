from flask import Flask, request
import logging
from WebhookHandlers import WebhookHandler

def create_app():
    app = Flask(__name__)
    handler = WebhookHandler()
    
    @app.route("/webhook", methods=["GET"])
    def verify_webhook():
        return handler.handle_verification(request.args)

    @app.route("/webhook", methods=["POST"])
    def handle_webhook():
        return handler.handle_incoming_message(request.json)

    return app

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    app = create_app()
    app.run(debug=True, port=80)