from flask import Flask, render_template, abort, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import SQLAlchemyError
import logging
from logging.handlers import RotatingFileHandler
import secrets

app = Flask(__name__)
app.config['DEBUG'] = False
app.secret_key = secrets.token_hex(32)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'  # SQLite database
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Disables modification tracking

# Initialize SQLAlchemy
db = SQLAlchemy(app)

# Define User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)

# ===== Logging Setup =====
handler = RotatingFileHandler('app.log', maxBytes=10000, backupCount=3)
handler.setLevel(logging.ERROR)
app.logger.addHandler(handler)

# ===== Error Handlers =====
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    app.logger.error(f"500 Error: {e}")
    return render_template('500.html'), 500

@app.errorhandler(Exception)
def handle_unexpected_error(e):
    app.logger.exception("Unhandled Exception")
    return redirect(url_for('error_500'))

# ===== Routes =====
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/divide/<int:a>/<int:b>')
def divide(a, b):
    try:
        result = a / b
        return f"Result: {result}"
    except ZeroDivisionError:
        flash("Cannot divide by zero!", "error")
        return redirect(url_for('home'))
    except Exception as e:
        app.logger.error(f"Math error: {e}")
        return redirect(url_for('error_500'))

@app.route('/force-error')
def force_error():
    try:
        return 1 / 0
    except Exception as e:
        app.logger.error(f"Forced error: {e}")
        return redirect(url_for('error_500'))

@app.route('/user/<int:user_id>')
def get_user(user_id):
    try:
        user = db.session.get(User, user_id)
        if not user:
            abort(404)
        return f"User: {user.name}"
    except SQLAlchemyError as e:
        app.logger.error(f"Database error: {e}")
        return redirect(url_for('error_500'))

@app.route('/500')
def error_500():
    return render_template('500.html'), 500

# Initialize database (only run once!)
# def initialize_database():
#     with app.app_context():
#         db.create_all()
#         # Add a test user if none exists
#         if not User.query.first():
#             user = User(name="Alice")
#             db.session.add(user)
#             db.session.commit()
#             print("Database initialized with test user 'Alice'")

if __name__ == '__main__':
    # initialize_database()  # Remove this after first run
    app.run()