from flask import Flask,render_template


app = Flask(__name__)


@app.route('/')
def home():
    return  render_template('index.html')
# def index():
#     return '<h1>Now it is Working!</h1>'


if(__name__) == "__main__":
    app.run()
