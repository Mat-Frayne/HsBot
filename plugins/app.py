"""."""
from flask import Flask
from flask import Flask, request, send_from_directory

app = Flask(__name__)


@app.route('/')
def index():
    """."""
    return "Hello World"


@app.route('/class/<c>')
def send_js(c):
    return send_from_directory('static/images/{}/'.format(c), "main.png")

if __name__ == '__main__':
    app.run(debug=True,
        host="0.0.0.0",
        port=80)
