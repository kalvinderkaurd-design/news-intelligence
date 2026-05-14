from flask import Flask, request, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from authlib.integrations.flask_client import OAuth
from werkzeug.middleware.proxy_fix import ProxyFix
from dotenv import load_dotenv
import os
from app.models import db, User

load_dotenv()

def create_app():
    """Application Factory."""
    app = Flask(__name__)
    
    # --- Configuration ---

    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-key-123')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Use SQLite for a fast, zero-config interview demo
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database/app.db'
    
    # Ensure the database directory exists
    db_dir = os.path.join(app.root_path, '..', 'database')
    if not os.path.exists(db_dir):
        os.makedirs(db_dir)




    # --- Production Fixes (Required for Railway) ---
    if os.getenv('RAILWAY_ENVIRONMENT'):
        from werkzeug.middleware.proxy_fix import ProxyFix
        app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)
        
        @app.before_request
        def force_https():
            if not request.is_secure:
                return redirect(request.url.replace('http://', 'https://', 1), code=301)



    # --- Initialize Extensions ---
    db.init_app(app)
    Migrate(app, db)
    
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    oauth = OAuth(app)
    google = oauth.register(
        name='google',
        client_id=os.getenv('GOOGLE_CLIENT_ID'),
        client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
        access_token_url='https://accounts.google.com/o/oauth2/token',
        authorize_url='https://accounts.google.com/o/oauth2/auth',
        api_base_url='https://www.googleapis.com/oauth2/v1/',
        userinfo_endpoint='https://openidconnect.googleapis.com/v1/userinfo',
        client_kwargs={'scope': 'openid email profile'},
        jwks_uri="https://www.googleapis.com/oauth2/v3/certs"
    )
    app.extensions['google_oauth'] = google

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # --- Blueprints ---
    from app.routes import auth_bp, main_bp, api_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp, url_prefix='/api')

    return app



