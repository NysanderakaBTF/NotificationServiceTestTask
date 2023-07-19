import os

from celery import shared_task, group

from .models import Notification, Message
from users.models import Client
import requests


@shared_task
def send_messages(notification_id, filter, message_text):
    print(filter)
    clients = Client.objects.all()
    if filter['operator_code'] is not None and len(filter['operator_code']) > 0:
        clients.filter(mobile_operator_code__in=filter.pop('operator_code'))

    if filter['tag'] is not None and len(filter['tag']) > 0:
        clients = clients.filter(tag__in=filter.pop('tag'))
    print(clients)
    tasks = []
    for client in clients:
        message = Message.objects.create(status=Message.StarusChoise.CREATED,
                                         client=client,
                                         dispatch_id=notification_id)
        tasks.append(send_one_message.s(message.pk, client.phone_number, message_text))
    result = group(tasks)()


@shared_task
def send_one_message(message_pk, phone, text):
    try:
        message = Message.objects.get(pk=message_pk)
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
