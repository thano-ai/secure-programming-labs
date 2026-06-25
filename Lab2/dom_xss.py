from flask import Flask, request, render_template, make_response
app = Flask(__name__)

# @app.after_request
# def apply_csp(response):
#     response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self';"
#     return response

@app.route('/')
def home():
    return render_template('dom_xss.html')


if __name__ == "__main__":
    app.run(debug=True)