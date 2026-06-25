from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    # if request.method == "POST":
    #     name = request.form['input']
    #     return render_template('index.html', name=name)
    return render_template('index.html')


@app.route('/test', methods=['POST'])
def test():
        name = request.form['input']
        return render_template('test.html', name=name)

if __name__ == '__main__':
    app.run(debug=True, port=8000)