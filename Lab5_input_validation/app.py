from flask import Flask, request, render_template, flash, redirect, url_for
import re
import secrets


app = Flask(__name__)
app.secret_key = secrets.token_hex(32)  # Needed for session

# Dummy users list for demo purposes
users = [
    {'username': 'user1', 'age': 25},
    {'username': 'user2', 'age': 30}
]

# Enhanced whitelist for username (allow letters, numbers, underscores, and dashes)
USERNAME_WHITELIST = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-")

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        # Fetch form data
        username = request.form.get("username").lower()
        age = request.form.get("age")
        message = request.form.get("message")
        email_input = request.form.get("email_input")
        password = request.form.get("password")

        validation_counter = 0

        # if not all(char in USERNAME_WHITELIST for char in username)

        if not all(char in USERNAME_WHITELIST for char in username):
            flash("Username contain unallowed characters", "error")
            validation_counter +=1
            # return redirect(url_for('home'))

        if len(username) < 3 or len(username) >=10 :
            flash("Invalid lenght, must be between 3 and 10", "error")
            validation_counter += 1
            # return redirect(url_for('home'))

        # Validate the age (numeric input, positive integer)
        if not age.isdigit() or int(age) <= 0 or int(age)> 100:
            flash("Invalid age! It must be a positive integer.", "error")
            validation_counter += 1
            # return redirect(url_for("home"))

        # Validate the length of the message
        if len(message) < 10 or len(message) > 200:
            flash("Message must be between 10 and 200 characters.", "error")
            validation_counter += 1
            # return redirect(url_for("home"))

        # Validate email input (basic email format regex)
        if not re.match(r'^[a-z0-9]+@[a-z]+\.[a-z]+$', email_input):
            flash("Invalid email format!", "error")
            validation_counter += 1
            # return redirect(url_for("home"))


        # Validate whitelist input (only allowed characters: letters, numbers, underscores, dashes)
        allowed_whitelist_chars = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_%^&*()!@#$")
        if not all(char in allowed_whitelist_chars for char in password):
            flash("Whitelist input contains invalid characters. Only letters, numbers, underscores, and dashes are allowed.", "error")
            validation_counter += 1
            # return redirect(url_for("home"))

        if len(password) < 8 or len(password) > 12:
            flash("Password must be between 8 and 12", "error")
            validation_counter += 1
            # return redirect(url_for("home"))

        # if password.startswith(username):
        #     flash("Password must not include the username", "error")
        #     return redirect(url_for("home"))

        if username in password:
            flash("Password must not include the username", "error")
            validation_counter += 1
            # return redirect(url_for("home"))

        if '123456' in password:
            flash("Series are not allowed", "error")
            validation_counter +=1

        # If all validations pass, proceed to simulate saving the user
        if validation_counter == 0:
            users.append({'username': username, 'age': int(age)})
            flash("User added successfully!", "success")
            return redirect(url_for("home"))


    return render_template("home.html", users=users)


if __name__ == "__main__":
    app.run(debug=True)
