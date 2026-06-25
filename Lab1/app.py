from flask import Flask, render_template, request

app = Flask(__name__)

# @app.route('/')
# def home():
#     return render_template('index.html')
    # return ("TEST")



# @app.route('/')
# def ali():
#     return render_template('index.html')
#
# # @app.route('/result', methods=['POST'])
# # def result():
# #     username = request.form['username']
# #     if username == "test":
# #         return render_template('result.html', user_name="Developer")
# #     else:
# #         return render_template('result.html', user_name="Student")
# #
# #     # return render_template('result.html', username=username)
# #     # return (x)
#
#
# @app.route('/test', methods=['POST'])
# def result():
#     name = request.form['test']
#
#     return render_template('result.html', username=name)
#
# @app.route('/user')
# def user():
#     return ("Hello user")
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/result', methods=['POST'])
def result():
     name = request.form['name']
     # name = name + " is your username"
     return render_template('result.html', data = name)

if __name__ == '__main__':
    app.run(debug=True, port=5001)

