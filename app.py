from celery.schedules import crontab
from api import init_api
from config import Config
from database import init_database
from flask import Flask, jsonify
from flask_cors import CORS, cross_origin
from mail import init_mail
from scheduled_jobs import celery, make_task
from mail.reminder import send_reminder_mail, send_monthly_report

app = Flask(__name__)
CORS(app, supports_credentials=True, resources={r"/api/*": {"origins": "*"}})
app.config.from_object(Config)
init_api(app)
init_database(app)
init_mail(app)
app.extensions['celery'] = celery
app.app_context().push()
celery.Task = make_task(app)


@app.route('/')
def hello_world():
    return jsonify({'message': 'Hello World!'})


@celery.task(name='time')
def current_time():
    from datetime import datetime
    print("Time current time is ", datetime.now())
    return datetime.now()


@celery.on_after_finalize.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(10.0, current_time.s(), name='time')
    sender.add_periodic_task(crontab(hour="20", minute="0"),
                             send_reminder_mail.s(),
                             name='send_reminder_mail')
    # sender.add_periodic_task(30.0, send_reminder_mail.s(), name='send_reminder_mail')
    sender.add_periodic_task(crontab(hour="8", minute="0", day_of_month="1"),
                             send_monthly_report.s(),
                             name='send_monthly_report')
    # sender.add_periodic_task(60.0, send_monthly_report.s(), name='send_monthly_report')


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
