# Generated by Django 3.2.4 on 2021-07-30 14:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_alter_user_introduce'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='introduce',
            field=models.TextField(blank=True, null=True),
        ),
    ]