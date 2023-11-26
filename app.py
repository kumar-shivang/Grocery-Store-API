from api import init_api
from config import Config
from database import init_database
from flask import Flask, jsonify
from flask_cors import CORS, cross_origin
from mail import init_mail

app = Flask(__name__)
CORS(app, supports_credentials=True, resources={r"/api/*": {"origins": "*"}})
app.config.from_object(Config)
init_api(app)
init_database(app)
init_mail(app)


@app.route('/')
def hello_world():
    return jsonify({'message': 'Hello World!'})


@app.route('/routes', methods=['GET'])
def routes():
    # This is a helper function to get all the routes in the app
    json = {}
    for rule in app.url_map.iter_rules():
        json[rule.endpoint] = rule.rule
    return jsonify(json)


# CORS() is not working so I have to add it manually
for endpoint, view_function in app.view_functions.items():
    app.view_functions[endpoint] = cross_origin()(view_function)
else:
    print('added cors')


if __name__ == '__main__':
    app.run()
