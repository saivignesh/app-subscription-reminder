# Local imports
from app import celery_app
from app import db, Apps, mail

# Flask imports
from flask import render_template
from flask_mail import Message

# Celery imports
from celery.schedules import crontab


@celery_app.on_after_finalize.connect
def setup_periodic_task(sender, **kwargs):
    sender.add_periodic_task(
        crontab(hour=13, minute=0),
        send_notification.s(),
    )


@celery_app.task()
def send_notification():
    msg = Message(
        subject="Subscription Reminders", recipients=["sai.s.vignesh@gmail.com"]
    )
    subs = db.session.query(Apps).all()
    filterSubs = list(filter(lambda x: x.daysleft < 4, subs))

    if filterSubs:
        msg.html = render_template("email.html", subs=subs, filterSubs=filterSubs)
        mail.send(msg)
        return f"Sent Notification"
    else:
        return f"No reminders necessary"
