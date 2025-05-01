from flask import Flask
from werkzeug.utils import quote  # Replaces deprecated url_quote

app = Flask(__name__)

@app.route('/')
def hello():
    return "Hello from Modern Flask App!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
