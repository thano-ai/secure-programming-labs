from datetime import datetime, timedelta
from flask import Flask, render_template, redirect, url_for, request, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import time
import secrets
from flask_limiter.errors import RateLimitExceeded

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)

# Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Flask-Limiter
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

# Mock DB
users = {
    'admin': {
        'username': 'admin',
        'password': generate_password_hash('admin123'),
        'role': 'admin',
        'login_attempts': 0,
        'locked_until': 0
    },
    'user1': {
        'username': 'user1',
        'password': generate_password_hash('password123'),
        'role': 'user',
        'login_attempts': 0,
        'locked_until': 0
    }
}

MAX_LOGIN_ATTEMPTS = 3
LOCKOUT_DURATION = 300  # 5 mins
IP_BLOCK_DURATION = 600  # 10 mins

# IP block list
blocked_ips = {}  # { ip: unblock_time }


class User(UserMixin):
    def __init__(self, user_dict):
        self.id = user_dict['username']
        self.username = user_dict['username']
        self.role = user_dict['role']


@login_manager.user_loader
def load_user(user_id):
    if user_id in users:
        return User(users[user_id])
    return None


# Unified IP block check
@app.before_request
def check_ip_block():
    ip = get_remote_address()
    if ip in blocked_ips:
        if datetime.now() < blocked_ips[ip]:
            remaining = int((blocked_ips[ip] - datetime.now()).total_seconds())
            return f"Too many login attempts from your IP. Try again in {remaining} seconds.", 429
        else:
            del blocked_ips[ip]


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/login', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def login():
    ip = get_remote_address()

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username not in users:
            flash('Invalid username or password', 'danger')
            return render_template('login.html')

        user_data = users[username]

        # Account lockout
        if user_data['locked_until'] > time.time():
            remaining_time = int(user_data['locked_until'] - time.time())
            flash(f'Account locked. Try again in {remaining_time} seconds.', 'danger')
            return render_template('login.html')

        # Verify password
        if check_password_hash(user_data['password'], password):
            user_data['login_attempts'] = 0
            user_data['locked_until'] = 0
            login_user(User(user_data))
            flash('Logged in successfully!', 'success')
            return redirect(url_for('profile'))
        else:
            user_data['login_attempts'] += 1
            if user_data['login_attempts'] >= MAX_LOGIN_ATTEMPTS:
                user_data['locked_until'] = time.time() + LOCKOUT_DURATION
                flash('Too many failed attempts. Account locked for 5 minutes.', 'danger')
            else:
                attempts_left = MAX_LOGIN_ATTEMPTS - user_data['login_attempts']
                flash(f'Invalid username or password. {attempts_left} attempts remaining.', 'danger')

    return render_template('login.html')


@app.errorhandler(429)
def ratelimit_handler(e):
    ip = get_remote_address()
    # If the IP is already in our block list, show remaining custom time
    if ip in blocked_ips:
        remaining = int((blocked_ips[ip] - datetime.now()).total_seconds())
        return f"Too many login attempts from your IP. Try again in {remaining} seconds.", 429
    # Otherwise, use Flask-Limiter's Retry-After header
    retry_after = request.headers.get("Retry-After")
    if retry_after:
        return f"Too many requests. Try again in {retry_after} seconds.", 429
    return "Too many requests. Try again later.", 429


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('home'))


@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html', user=current_user)


@app.route('/admin')
@login_required
def admin():
    if current_user.role == 'admin':
        return render_template('admin.html', user=current_user)
    flash('You do not have permission to access this page', 'danger')
    return redirect(url_for('profile'))


if __name__ == '__main__':
    app.run(debug=True)
