"""
AI Resume Screening System — Application Entry Point
=====================================================
Run:  python app.py
Then visit http://127.0.0.1:5000 in your browser.
"""

import os
import sys

# Ensure project root is on the Python path
ROOT_DIR = os.path.abspath(os.path.dirname(__file__))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(ROOT_DIR, '.env'))
except ImportError:
    pass

from flask import Flask


def create_app() -> Flask:
    app = Flask(
        __name__,
        template_folder=os.path.join(ROOT_DIR, 'web_app', 'templates'),
        static_folder=os.path.join(ROOT_DIR, 'web_app', 'static'),
    )
    app.secret_key = os.environ.get('SECRET_KEY', 'ai-resume-screener-secret-key-2024')
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB

    # Database config
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    from models import db
    db.init_app(app)
    
    with app.app_context():
        db.create_all()

    # Optional Google OAuth config (set these env vars for real SSO)
    app.config['GOOGLE_CLIENT_ID'] = os.environ.get('GOOGLE_CLIENT_ID', '')
    app.config['GOOGLE_CLIENT_SECRET'] = os.environ.get('GOOGLE_CLIENT_SECRET', '')

    # Register routes blueprint
    from web_app.routes import main
    app.register_blueprint(main)

    # Initialize auth (SSO + demo login)
    from web_app.auth import init_auth
    init_auth(app)

    return app


if __name__ == '__main__':
    application = create_app()
    print("\n" + "=" * 55)
    print("  AI Resume Screening System")
    print("  Open http://127.0.0.1:5001 in your browser")
    print("=" * 55 + "\n")
    application.run(debug=True, port=5001)
