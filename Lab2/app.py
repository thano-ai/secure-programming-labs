from flask import Flask, request, render_template, make_response
import bleach
app = Flask(__name__)
messages = []

# Content Security Policy
@app.after_request
def set_csp(response):

    response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'none'"
    return response

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/vulnerable", methods=["GET", "POST"])
def vulnerable():
    if request.method == "POST":
        x = request.form.get("message")
        # clean_x = bleach.clean(x)
        messages.append(x)  # NO sanitization = vulnerable
    return render_template("vulnerable.html", x=messages)

@app.route("/secure", methods=["GET", "POST"])
def secure():
    if request.method == "POST":
        name = request.form.get("name")
        # Sanitize input before storing
        clean_name = bleach.clean(name)
        messages.append(clean_name)
    response = make_response(render_template("secure.html", messages=messages))
    return response

if __name__ == "__main__":
    app.run(debug=True)
