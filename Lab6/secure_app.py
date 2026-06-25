from flask import Flask, request, render_template
import os

app = Flask(__name__)

# Define the safe base directory
BASE_DIR = os.path.abspath("files")



# Absolute path to the secret file to restrict files/secret.txt
SECRET_FILE = os.path.abspath(os.path.join(BASE_DIR, "secret.txt"))


@app.route("/")
def index():
    filename = request.args.get("file")

    if filename:
        # Safely join the user input with the base directory
        ## ../app/py
        requested_path = os.path.abspath(os.path.join(BASE_DIR, filename))

        # Check if the file is outside the allowed directory
        if not requested_path.startswith(BASE_DIR):
            content = "Access Denied: Invalid path."
        # Check if the requested file is the secret.txt
        elif requested_path == SECRET_FILE:
            content = "Access Denied: You are not allowed to access this file."

        else:
            try:
                with open(requested_path, "r") as f:
                    content = f.read()
            except FileNotFoundError:
                content = "File not found!"
            except Exception as e:
                content = f"Error: {str(e)}"
    else:
        content = "No file selected."
    if content == "No file selected.":
        return render_template("index.html", content=content)
    else:
        return render_template("outbot.html", content=content)

if __name__ == "__main__":
    app.run(debug=True)
