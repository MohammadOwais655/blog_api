# Generated by Django 4.2.14 on 2024-07-25 10:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0004_alter_usersuggestiontopic_topic'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='is_two_factor_auth',
            field=models.BooleanField(default=False),
        ),
    ]
