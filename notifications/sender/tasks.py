import os

from celery import shared_task, group

from sender.models import Notification, Message
from users.models import Client
import requests


@shared_task
def send_messages(notification: Notification):
    filter = notification.filer
    clients = Client.objects.filter(mobile_operator_code__in=filter.pop('mobile_operator_code'),
                                    tag__in=filter.pop('tag'))
    tasks = []
    for client in clients:
        message = Message.objects.create(status=Message.StarusChoise.CREATED,
                                         client=client,
                                         dispatch=notification)
        tasks.append(send_one_message.s(message, client.phone_number, notification.message_text))
    result = group(tasks)()


@shared_task
def send_one_message(message: Message, phone, text):
    try:
        message.status = message.StarusChoise.PROCESSING
        message.save()
        # response = requests.post('https://probe.fbrq.cloud/send/%s' % message.id,
        #                          headers={'Content-Type': 'application/json',
        #                                   'Authorization': 'Bearer ' + os.getenv('TASK_TOKEN')},
        #                          json={
        #                              'id': message.id,
        #                              'phone': phone,
        #                              "text": text
        #                          }
        #                          )
        print("AAAAAAAAAAAAAAAAAAAAAAAAAA")
        message.status = message.StarusChoise.COMPLETE
        message.save()
    except requests.exceptions.RequestException:
        message.status = Message.StarusChoise.ERROR

