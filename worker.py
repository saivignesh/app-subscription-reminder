# Celery imports
from celery import Celery,Task
from celery.schedules import crontab

def make_celery(app):
    class FlaskTask(Task):
        def __call__(self,*args,**kwargs):
            with app.app_context():
                return self.run(*args,**kwargs)
        
    celery_app = Celery(
        "emailer",
        task_cls=FlaskTask,
        broker=app.config['CELERY_BROKER_URL'],
        backend=app.config['CELERY_RESULT_BACKEND'],
        include=['tasks'],
        result_expires=3600       
    )

    celery_app.set_default()
    #app.conf.update(result_expires=3600)
    app.extensions["celery"] = celery_app
    celery_app.conf.timezone = "Asia/Kolkata"
    
    return celery_app