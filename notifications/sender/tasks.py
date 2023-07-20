import datetime
import json
import os
import smtplib
import ssl
import time

from celery import shared_task, group
from django.contrib.auth.models import User
from django_celery_results.models import TaskResult

from .models import Notification, Message
from users.models import Client
import requests


@shared_task
def send_messages(notification_id, filter, message_text):
    # print(filter)

    filtered_q = {}
    if filter['operator_code'] is not None:
        filtered_q.setdefault('mobile_operator_code__in', filter['operator_code'])
    if filter['tag'] is not None:
        filtered_q.setdefault('tag__in', filter['tag'])

    clients = Client.objects.filter(**filtered_q)
    tasks = []
    for client in clients:
        try:
            message = Message.objects.create(status=Message.StarusChoise.CREATED,
                                             client=client,
                                             dispatch_id=notification_id)
            tasks.append(send_one_message.s(message.pk, client.phone_number, message_text))
        except Exception as e:
            print(e)
    result = group(tasks)()
    return result


@shared_task
def send_one_message(message_pk, phone, text):
    message = None
    try:
        message = Message.objects.get(pk=message_pk)
        message.status = message.StarusChoise.PROCESSING
        message.save()
        try:
            response = requests.post('https://probe.fbrq.cloud/send/%s' % message.id,
                                     headers={'Content-Type': 'application/json',
                                              'Authorization': 'Bearer ' + os.getenv('TASK_TOKEN')},
                                     json={
                                         'id': message.id,
                                         'phone': phone,
                                         "text": text
                                     }
                                     )
            message.status = message.StarusChoise.COMPLETE
            message.save()
            return {
                'id': message.id,
                'phone': phone,
                "text": text
            }
        except Exception as e:
            message.status = Message.StarusChoise.ERROR
            message.save()
    except Exception as e:
        # print(e)
        raise e


@shared_task
def send_daily_stats():
    users = [i['email'] for i in User.objects.all().values('email') if i['email'] != '']


    dt = datetime.datetime.now()

    year = dt.year
    month = dt.month
    day = dt.day

    task_results = TaskResult.objects.filter(
        date_done__gte=datetime.date(
            year,
            month,
            day
        ),
        date_done__lt=datetime.date(
            year,
            month,
            day+1
        )
    )

    answer = ''

    for i in task_results:
        # print(str(i))
        # print(i.result)
        res = json.loads(i.result)
        if isinstance(res, list):

            answer+= "Completed message sending task: " + str(i.__dict__)+ "\n With messages:\n"
            ids =[]
            # print('AAA!!!!')
            for j in res[1]:
                ids.append(j[0][0])
            # print(ids)
            for j in task_results:
                for k in ids:
                    if j.task_id==k:
                        answer+=str(j.__dict__)+'\n'
    print(users)
    if answer != '':
        session = smtplib.SMTP(os.getenv('EMAIL_HOST'), int(os.getenv('EMAIL_PORT')))
        session.starttls()
        session.login(os.getenv('EMAIL_HOST_USER'), os.getenv('EMAIL_HOST_PASSWORD'))
        msg = f'From: {os.getenv("EMAIL_HOST_USER")}\r\nTo: {users}\r\nContent-Type: text/plain; charset="utf-8"\r\nSubject: Message sending stats\r\n\r\n'
        msg += answer
        # print(msg)
        session.sendmail(os.getenv('EMAIL_HOST_USER'), users, msg)
        session.quit()




