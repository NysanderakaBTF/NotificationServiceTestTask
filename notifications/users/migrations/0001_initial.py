# Generated by Django 4.2.3 on 2023-07-18 11:46

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Client',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('phone_number', models.CharField(max_length=11, unique=True)),
                ('mobile_operator_code', models.CharField(max_length=10)),
                ('tag', models.CharField(max_length=255)),
                ('timezone', models.CharField(max_length=255)),
            ],
        ),
    ]
