from flask import Flask, render_template, request, session, redirect, url_for, flash
from flask_wtf.csrf import CSRFProtect
from wtforms import Form, StringField, IntegerField, validators
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)  # Needed for session
app.config['WTF_CSRF_SECRET_KEY'] = secrets.token_hex(32)  # Separate key for CSRF
csrf = CSRFProtect(app)  # Enable CSRF protection globally

# Mock database
users = {
    'alice': {'password': 'pass123', 'balance': 1000},
    'bob': {'password': 'pass456', 'balance': 500},
    'ali': {'password': '12345', 'balance': 0}

}


class TransferForm(Form):
    recipient = StringField('recipient', [
        validators.InputRequired(),
        validators.length(min=3, max=10)
    ])

    amount = IntegerField('amount', [
        validators.InputRequired(),
        validators.NumberRange(min=100, max=1000)
    ])


@app.route('/')
def home():
    if 'username' in session:
        form = TransferForm()  # Empty form for GET requests
        return render_template('secure_home.html',
                               username=session['username'],
                               balance=users[session['username']]['balance'],
                               form=form)
    return render_template('secure_login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username in users and users[username]['password'] == password:
            session['username'] = username
            flash('Login successful!', 'success')
            return redirect(url_for('home'))
        flash('Invalid credentials', 'danger')
    return render_template('secure_login.html')


@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('You have been logged out', 'info')
    return redirect(url_for('home'))


@app.route('/transfer', methods=['POST'])
def transfer():
    if 'username' not in session:
        return redirect(url_for('login'))

    form = TransferForm(request.form)

    if form.validate():
        # Process transfer (same as before)
        amount = int(request.form['amount'])
        recipient = request.form['recipient']

        if recipient not in users:
            return "Recipient Not found", 404

        if amount > users[session['username']]['balance']:
            return "Insufficient Fund", 400

        users[session['username']]['balance'] -= amount
        users[recipient]['balance'] += amount
        return redirect(url_for('home'))

    # If validation fails, redisplay home with errors
    return render_template('secure_home.html',
                           username=session['username'],
                           balance=users[session['username']]['balance'],
                           form=form)


if __name__ == '__main__':
    app.run(debug=True, port=5000)
