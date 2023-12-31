# Generated by Django 4.2.3 on 2023-07-18 17:04

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('sender', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='message',
            name='dispatch',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='messages', to='sender.notification'),
        ),
        migrations.AlterField(
            model_name='message',
            name='status',
            field=models.CharField(choices=[('CREATED', 'Created'), ('PROCESSING', 'Processing'), ('COMPLETE', 'Complete'), ('ERROR', 'Error')], default='CREATED', max_length=20),
        ),
        migrations.AlterField(
            model_name='notification',
            name='message_text',
            field=models.TextField(max_length=255),
        ),
    ]
