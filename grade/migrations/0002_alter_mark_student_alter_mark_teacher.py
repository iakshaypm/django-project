# Generated by Django 5.0.4 on 2024-04-19 06:16

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('grade', '0001_initial'),
        ('user', '0003_alter_account_is_staff'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mark',
            name='student',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='student_id', to='user.student'),
        ),
        migrations.AlterField(
            model_name='mark',
            name='teacher',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='user.teacher'),
        ),
    ]
