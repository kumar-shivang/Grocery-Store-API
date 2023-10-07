from flask import Flask, jsonify
from api import init_api
from database import init_database
from config import Config

# from authorization import init_auth

app = Flask(__name__)
app.config.from_object(Config)
init_api(app)
init_database(app)


# init_auth(app)


@app.route('/')
def hello_world():  # put application's code here
    return jsonify({'message': 'Hello World!'})


@app.route('/routes')
def routes():
    json = {}
    for rule in app.url_map.iter_rules():
        json[rule.endpoint] = rule.rule
    return jsonify(json)


if __name__ == '__main__':
    app.run()
