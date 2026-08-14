from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import time
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)

# Configure SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)

# Configure Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Configure Flask-Limiter
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

# Account lockout configuration
MAX_LOGIN_ATTEMPTS = 3
LOCKOUT_DURATION =  120 # 5 minutes

# Database model
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(50), nullable=False, default='user')
    login_attempts = db.Column(db.Integer, default=0)
    locked_until = db.Column(db.Float, default=0.0)

    def check_password(self, password):
        return check_password_hash(self.password, password)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# Initialize database and create a default admin user
@app.before_request
def create_tables():
    db.create_all()

    if not User.query.first():
        admin_user = User(
            username='admin',
            password=generate_password_hash('admin123'),
            role='admin'
        )

        user1 = User(
            username='user1',
            password=generate_password_hash('password123'),
            role='user'
        )
        db.session.add(admin_user)
        db.session.add(user1)
        db.session.commit()


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/login', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()
        if not user:
            flash('Invalid username or password', 'danger')
            return render_template('login.html')

        if user.locked_until > time.time():
            remaining_time = int(user.locked_until - time.time())
            flash(f'Account locked. Try again in {remaining_time} seconds.', 'danger')
            return render_template('login.html')

        if user.check_password(password):
            user.login_attempts = 0
            user.locked_until = 0
            db.session.commit()
            login_user(user) ## current user
            flash('Logged in successfully!', 'success')
            # next_page = request.args.get('next')
            return redirect(url_for('profile'))
        else:
            user.login_attempts += 1
            if user.login_attempts >= MAX_LOGIN_ATTEMPTS:
                user.locked_until = time.time() + LOCKOUT_DURATION
                flash('Too many failed attempts. Account locked for 5 minutes.', 'danger')
            else:
                attempts_left = MAX_LOGIN_ATTEMPTS - user.login_attempts
                flash(f'Invalid username or password. {attempts_left} attempts remaining.', 'danger')
            db.session.commit()


    return render_template('login.html')


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
        users = User.query.all()
        return render_template('admin.html', user=current_user, users=users)
    flash('You do not have permission to access this page', 'danger')
    return redirect(url_for('profile'))

@app.route('/admin/add', methods=['GET', 'POST'])
@login_required
def add_user():
    if current_user.role != 'admin':
        flash('Unauthorized', 'danger')
        return redirect(url_for('profile'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']

        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'danger')
            return redirect(url_for('add_user'))

        new_user = User(
            username=username,
            password=generate_password_hash(password),
            role=role
        )
        db.session.add(new_user)
        db.session.commit()
        flash('User added successfully!', 'success')
        return redirect(url_for('admin'))

    return render_template('add_user.html')

@app.route('/admin/edit/<int:user_id>', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    if current_user.role != 'admin':
        flash('Unauthorized', 'danger')
        return redirect(url_for('profile'))

    user = User.query.get_or_404(user_id)

    if request.method == 'POST':
        user.username = request.form['username']
        password = request.form['password']
        if password:
            user.password = generate_password_hash(password)
        user.role = request.form['role']
        db.session.commit()
        flash('User updated successfully!', 'success')
        return redirect(url_for('admin'))

    return render_template('edit_user.html', user=user)

@app.route('/admin/delete/<int:user_id>', methods=['POST'])
@login_required
def delete_user(user_id):
    if current_user.role != 'admin':
        flash('Unauthorized', 'danger')
        return redirect(url_for('profile'))

    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash('You cannot delete yourself!', 'danger')
        return redirect(url_for('admin'))

    db.session.delete(user)
    db.session.commit()
    flash('User deleted successfully!', 'success')
    return redirect(url_for('admin'))


if __name__ == '__main__':
    app.run(debug=True)
