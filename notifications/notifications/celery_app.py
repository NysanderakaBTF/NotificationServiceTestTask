import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'notifications.settings')


app = Celery('notifications')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()

app.conf.beat_schedule = {
    'send-stats': {
        'task': 'sender.tasks.send_daily_stats',
        'schedule': crontab(minute='59', hour='23')
    },
}