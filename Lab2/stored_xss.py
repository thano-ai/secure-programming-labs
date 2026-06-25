from flask import Flask, render_template, request
import bleach

app = Flask(__name__)
comments = []

# @app.route("/", methods=["GET", "POST"])
# def index():
#     if request.method == "POST":
#         comment = request.form.get("comment")
#         comments.append(comment)  # No sanitization
#     return render_template("comment.html", comments=comments)

@app.after_request
def apply_csp(response):
    response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self';"
    return response
#
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        comment = request.form.get("comment")
        clean_comment = bleach.clean(comment)
        comments.append(clean_comment)
    return render_template("comment.html", comments=comments)


if __name__ == "__main__":
    app.run(debug=True)
