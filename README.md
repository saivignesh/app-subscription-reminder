# Description 

This is a small CRUD application that records multiple subscriptions and sends notification via email when the due date for any of the subscriptions is drawing near ( < 4 days).

# Motivation

I wanted to practice implementing `celery` workers and scheduling periodic tasks using `celery` workers. So I came up with this simple app that tracks number of days left in a subscription and sends notification via mail.  The notification is handled by a scheduled task in `celery`. 

# Tech Stack

## Backend

1. Flask : WSGI
	1. Flask-SQLAlchemy
	2. Flask-mail
2. Celery: Background Jobs
3. Redis: Broker + Result backend
4. Jinja : Template engine
5. SQLite: Database

## Frontend

1. Bootstrap


# Main Lessons

## Hybrid Property

While designing the subscriptions model class, I was wondering how to obtain the number of days left in a subscription. The options were to: 
	1. Explicitly calculate this value when needed from the other columns in the table.
	2. Make it a column directly in the table and use a separate method in the class to calculate it.
	3. Define it as a generated or computed column ( Pure SQL ).

While searching for a solution to this task, I came across the `@hybrid_property` decorator for the `db.Model` class that conveniently allows us to access the computed value as a class instance attribute while also facilitating use with database queries and operations like a table column.

```python
class Apps(db.Model):
    __tablename__ = "apps"
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String,nullable=False)
    amount = db.Column(db.Float,nullable=False)
    subtype = db.Column(db.String, nullable=False)
    subdate = db.Column(db.Date,nullable=False)
    expdate = db.Column(db.Date)
    subdays = db.Column(db.Integer)    

    def setdays(self):
        if self.expdate:
            self.subdays = (self.expdate-self.subdate).days
    
    def setexpdate(self):
        if self.subdays:
            self.expdate = self.subdate + timedelta(self.subdays)

    @hybrid_property
    def daysleft(self):
        return (self.expdate - date.today()).days
```

## Flask Mail with Gmail

I imagined setting up an SMTP server for the application will be complicated. But it was easier than expected, especially using a normal Gmail account. 

To login to the gmail account, we have to use the app password provided by google instead of the normal password registered with the account. More details [here](https://support.google.com/mail/answer/185833?hl=en)

```python
MAIL_SERVER = 'smtp.gmail.com'
MAIL_PORT = 587
MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
MAIL_DEFAULT_SENDER = os.environ.get("MAIL_USERNAME")
MAIL_USE_TLS = True
MAIL_USE_SSL = False
```

Copy and paste the app password provided by google into an environment variable.


## Celery Tasks

Setting up a celery app and defining the tasks were quite straight forward. 

```python
@celery_app.on_after_finalize.connect
def setup_periodic_task(sender,**kwargs):
    sender.add_periodic_task(
        crontab(hour=3,minute=0),
        send_notification.s(),
    )

@celery_app.task()
def send_notification():
    msg = Message(
        subject="Subscription Reminders",
        recipients=["sai.s.vignesh@gmail.com"]
    )
    subs = db.session.query(Apps).all()
    filterSubs = list(filter(lambda x: x.daysleft < 4,subs))

    if filterSubs:
        msg.html = render_template("email.html",subs=subs,filterSubs=filterSubs)
        mail.send(msg)
        return f"Sent Notification"
    else:
        return f"No reminders necessary"

```

The main task is `send_notification`. Note that in this case both sender and recipient of the mail is myself. But recipient can be a different email added with each subscription.

Here I am not directly filtering while querying because I also want to send number of days left for all subscriptions along with the ones that are due in a few days.

`crontab` schedules this task to run daily at 3:00 am. If there are subscriptions due a mail will be sent and return "Sent Notification" otherwise the task will simply return "No reminders necessary".

Another important thing to note is that celery uses UTC by default. To set local timezone, we have to update the celery app configuration.

```python
celery_app.conf.timezone = "Asia/Kolkata"
```

With this we can start the celery worker and celery beat and the application should work fine.

### Daemonization 

At this point, I was also interested in seeing if it was possible to run the workers and the beat in the background on system startup instead of typing the celery worker and celery beat commands every time. 

Fortunately, [Celery](https://docs.celeryq.dev/en/stable/userguide/daemonizing.html#daemonizing) documentation provides a detailed process to setup a `systemctl` service to run on system startup.

The configuration for the worker and beat are stored in `/etc/default/celeryd` . 

The actual service files for the worker and beat are stored in `/etc/systemd/system/celery.service` and `/etc/systemd/system/celerybeat.service` respectively.

All the files used to set up the daemonization are in [systemd](systemd) folder.





