from flask import Flask, request, render_template

app = Flask(__name__)


@app.route("/")
def index():
    filename = request.args.get("file")

    if filename:

        if filename == "secret.txt":
            content = "Access Denied: You are not authorized to view this file."
        else:
            try:

                ### info.txt
                ### files/input.txt
                ### ../app.py
                ####../app.py
                with open(f"files/{filename}", "r") as f:
                    content = f.read()
            except FileNotFoundError:
                content = "File not found!"
            except Exception as e:
                content = f"Error: {e}"
    else:
        content = "No file selected."

    return render_template("index.html", content=content)


if __name__ == "__main__":
    app.run(debug=True)
