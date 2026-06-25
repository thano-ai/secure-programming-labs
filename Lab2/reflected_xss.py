from flask import Flask, render_template, request
import bleach
app = Flask(__name__)

@app.route("/search")
def search():
    query = request.args.get("q")
    clean_query = bleach.clean(query)
    return f"<h2>Results for: {clean_query}</h2>"  # Injects raw input

# @app.route("/search")
# def search():
#     query = request.args.get("q", "")
#     clean_query = bleach.clean(query)
#     return render_template("search.html", query=clean_query)

if __name__ == "__main__":
    app.run(debug=True)
