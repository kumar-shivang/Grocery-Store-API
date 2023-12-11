from celery import Celery, Task


def make_task(app):
    class FlaskTask(Task):
        def __call__(self, *args, **kwargs):
            print('task called')
            with app.app_context():
                return self.run(*args, **kwargs)
    return FlaskTask


celery = Celery('__main__', broker='redis://localhost:6379/1', backend='redis://localhost:6379/2')
celery.conf.timezone = "Asia/Kolkata"





