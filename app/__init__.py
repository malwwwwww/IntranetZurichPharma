from flask import Flask
from .config import Config
from .routes.auth import auth_bp
from .routes.documents import documents_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Registrar blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(documents_bp)

    return app