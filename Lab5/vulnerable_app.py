from flask import Flask, request, render_template, redirect, url_for, session
import sqlite3

app = Flask(__name__)
app.secret_key = "supersecret"  # Needed for sessions


def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (username TEXT, password TEXT, role TEXT)''')
    # Predefined users
    c.execute("INSERT INTO users (username, password, role) VALUES ('admin', 'admin123', 'admin')")
    c.execute("INSERT INTO users (username, password, role) VALUES ('john', 'johnpass', 'user')")
    conn.commit()
    conn.close()


init_db()


@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        # query = F"select * from users where username = '{username}' and password = '{password}'"
        # conn = sqlite3.connect("users.db")
        # c = conn.cursor
        # c.execute(query)
        #
        # db_user = c.fetchone() ## [admin, admin123, admin]
        #
        # if db_user:
        #     session['username'] = db_user[0]
        #     session['role'] = db_user[2]
        #     return redirect(url_for('home'))
        # else:
        #     return "Login failed"

        # query = f"select * from users where username = '{username}' and password = '{password}'"
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        query = f"select * from users where username = '{username}' and password = '{password}'"
        c.execute(query)

        user = c.fetchone() # [admin, admin123, admin]
        conn.close()

        if user:
            session['username'] = user[0]
            session['role'] = user[2]
            return redirect(url_for("dashboard"))
        else:
            return "Login failed!"

    return render_template("login_vulnerable.html")


@app.route("/dashboard")
def dashboard():
    if 'username' not in session:
        return redirect(url_for("login"))
    # username = session['username']
    # role = session['role']

    if session['role'] == "admin":
        conn = sqlite3.connect("users.db")
        c = conn.cursor()
        c.execute("select username, role from users")
        users = c.fetchall()
        return render_template('dashboard_vulnerable.html', username= session['username'], role=session['role'], users=users)
    else:
        conn = sqlite3.connect("users.db")
        c = conn.cursor()
        c.execute(f"select * from users where username = '{session['username']}'")
        user = c.fetchone()
        return render_template('dashboard_vulnerable.html', username= session['username'], role=session['role'], users=user)


    # if session['role'] == "user":
    #     return render_template("dashboard_vulnerable.html", username=session['username'], role=session['role'], users=None)
    #
    # else:
    #    conn = sqlite3.connect('users.db')
    #    c = conn.cursor()
    #    query = "SELECT * FROM USERS"
    #    c.execute(query)
    #    db_users = c.fetchall()
    #    return render_template("dashboard_vulnerable.html", username=session['username'], role=session['role'],
    #                            users=db_users)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)
