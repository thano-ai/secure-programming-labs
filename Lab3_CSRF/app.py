from flask import Flask, request, render_template, session, redirect, url_for
app = Flask(__name__)
app.secret_key = 'secret-key'

# Mock database
users = {
    'alice': {'password': 'pass123', 'balance': 1000},
    'bob': {'password': 'pass456', 'balance': 500},
    'ali': {'password': '12345', 'balance': 0}
}


@app.route('/')
def home():
    if 'username' in session:
        return render_template('vulnerable_home.html',
                               username=session['username'],
                               balance=users[session['username']]['balance'])
    return render_template('vulnerable_login.html')


@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    if username in users and users[username]['password'] == password:
        session['username'] = username
        return redirect(url_for('home'))
    return "Invalid credentials", 401


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('home'))


# Vulnerable transfer endpoint - no CSRF protection
@app.route('/transfer', methods=['POST'])
def transfer():
    if 'username' not in session:
        return redirect(url_for('home'))

    amount = int(request.form['amount'])
    recipient = request.form['recipient']

    if recipient not in users:
        return "Recipient not found", 404

    if amount > users[session['username']]['balance']:
        return "Insufficient funds", 400

    users[session['username']]['balance'] -= amount
    users[recipient]['balance'] += amount

    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True, port=5000)