"""
Authentication module — Google OAuth SSO + demo login.
Uses flask-login for session management and authlib for Google OAuth.
"""

import os
import functools

from flask import (
    Blueprint, render_template, request, redirect,
    url_for, flash, session,
)

try:
    from flask_login import (
        LoginManager, UserMixin, login_user, logout_user,
        login_required, current_user,
    )
    HAS_FLASK_LOGIN = True
except ImportError:
    HAS_FLASK_LOGIN = False

try:
    from authlib.integrations.flask_client import OAuth
    HAS_AUTHLIB = True
except ImportError:
    HAS_AUTHLIB = False

auth = Blueprint('auth', __name__)

from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User

# ---------- Setup ---------- #

login_manager = None
oauth = None
google = None


def init_auth(app):
    """Initialize auth on the Flask app."""
    global login_manager, oauth, google

    if HAS_FLASK_LOGIN:
        login_manager = LoginManager()
        login_manager.login_view = 'auth.login'
        login_manager.login_message = 'Please log in to access this page.'
        login_manager.login_message_category = 'info'
        login_manager.init_app(app)

        @login_manager.user_loader
        def load_user(user_id):
            try:
                return User.query.get(int(user_id))
            except ValueError:
                return None

    # Google OAuth (optional — works if credentials are set)
    google_client_id = app.config.get('GOOGLE_CLIENT_ID', os.environ.get('GOOGLE_CLIENT_ID', ''))
    google_client_secret = app.config.get('GOOGLE_CLIENT_SECRET', os.environ.get('GOOGLE_CLIENT_SECRET', ''))

    if HAS_AUTHLIB and google_client_id and google_client_secret:
        oauth = OAuth(app)
        google = oauth.register(
            name='google',
            client_id=google_client_id,
            client_secret=google_client_secret,
            server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
            client_kwargs={'scope': 'openid email profile'},
        )

    app.register_blueprint(auth)


def login_required_decorator(f):
    """Custom login_required that works with or without flask-login."""
    if HAS_FLASK_LOGIN:
        from flask_login import login_required as flask_lr
        return flask_lr(f)

    @functools.wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('user_id'):
            flash('Please log in to access this page.', 'info')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated


def get_current_user():
    """Get the current logged-in user (works with or without flask-login)."""
    if HAS_FLASK_LOGIN:
        from flask_login import current_user
        if current_user.is_authenticated:
            return current_user
        return None
    user_id = session.get('user_id')
    if user_id:
        try:
            return User.query.get(int(user_id))
        except ValueError:
            session.pop('user_id', None)
            return None
    return None


# ---------- Routes ---------- #

@auth.route('/register', methods=['GET', 'POST'])
def register():
    user = get_current_user()
    if user:
        return redirect(url_for('main.home'))

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '').strip()

        if not name or not email or not password:
            flash('All fields are required.', 'danger')
            return render_template('register.html')

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email address is already registered. Please log in.', 'warning')
            return redirect(url_for('auth.login'))

        new_user = User(
            email=email,
            name=name,
            password_hash=generate_password_hash(password)
        )
        db.session.add(new_user)
        db.session.commit()

        flash('Account created successfully! Please log in.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('register.html')


@auth.route('/login', methods=['GET', 'POST'])
def login():
    user = get_current_user()
    if user:
        return redirect(url_for('main.home'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '').strip()

        user = User.query.filter_by(email=email).first()

        if user and user.password_hash and check_password_hash(user.password_hash, password):
            if HAS_FLASK_LOGIN:
                login_user(user, remember=True)
            else:
                session['user_id'] = user.id
            flash(f'Welcome back, {user.name}!', 'success')
            next_page = request.args.get('next', url_for('main.home'))
            return redirect(next_page)
        elif user and not user.password_hash:
            flash('This account was created via Google. Please use Continue with Google.', 'warning')
        else:
            flash('Invalid email or password.', 'danger')

    has_google = google is not None
    return render_template('login.html', has_google=has_google)


@auth.route('/login/google')
def login_google():
    if google is None:
        flash('Google SSO is not configured.', 'warning')
        return redirect(url_for('auth.login'))
    redirect_uri = url_for('auth.google_callback', _external=True)
    return google.authorize_redirect(redirect_uri)


@auth.route('/login/google/callback')
def google_callback():
    if google is None:
        return redirect(url_for('auth.login'))

    try:
        token = google.authorize_access_token()
        userinfo = token.get('userinfo')
        if not userinfo:
            userinfo = google.parse_id_token(token, None)

        email = userinfo.get('email', '')
        name = userinfo.get('name', email.split('@')[0])
        picture = userinfo.get('picture', '')

        # Lookup or Create user
        user = User.query.filter_by(email=email).first()
        if not user:
            user = User(
                email=email,
                name=name,
                avatar_url=picture,
                sso_provider='google'
            )
            db.session.add(user)
        else:
            # Sync avatar if missing, and ensure sso_provider is set
            if not user.avatar_url:
                user.avatar_url = picture
            if user.sso_provider != 'google':
                user.sso_provider = 'google'
                
        db.session.commit()

        if HAS_FLASK_LOGIN:
            login_user(user, remember=True)
        else:
            session['user_id'] = user.id

        flash(f'Welcome, {user.name}!', 'success')
        return redirect(url_for('main.home'))

    except Exception as e:
        flash(f'Google login failed: {str(e)}', 'danger')
        return redirect(url_for('auth.login'))


@auth.route('/logout')
def logout():
    if HAS_FLASK_LOGIN:
        logout_user()
    session.pop('user_id', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.home'))


# ---------- Context Processor ---------- #

@auth.app_context_processor
def inject_user():
    """Make current_user available in all templates."""
    return {'current_user_data': get_current_user()}
