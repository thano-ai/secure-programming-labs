from flask import Flask, request, render_template, session, redirect, url_for
import secrets
app = Flask(__name__)
app.secret_key = secrets.token_hex(32)

# Mock database
users = {
    'user1': {'password': '1234', 'documents': [1, 3]},
    'user2': {'password': 'pass2', 'documents': [2]},

}

documents = {
    1: {"owner": "user1", "content": "this is content"},
    2: {"owner": "user2", "content": "Secret document 2"},
    3: {"owner": "user1", "content": "Secret document 3"}
}

@app.route('/')
def home():
    if 'username' in session:
        doc_ids = users[session['username']]['documents']

        return render_template('dashboard.html', username=session['username'], document_ids=doc_ids)
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    form_password = request.form['password']

    if username in users and users[username]['password'] == form_password:
        session['username'] = username
        return redirect(url_for('home'))

    return "Invalid Credentials", 403


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('home'))


@app.route('/document/<int:doc_id>')
def view_document(doc_id):
    if 'username' not in session:
        return redirect(url_for('home'))

    if doc_id not in documents:
        return "Document not found", 404

    document = documents[doc_id]
    return render_template('document.html', username=session['username'], document=document, doc_id=doc_id)



if __name__ == '__main__':
    app.run(debug=True, port=5000)