# Generated by Django 5.0.4 on 2024-04-21 04:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('attendance', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mainattendance',
            name='attendance_type',
            field=models.PositiveIntegerField(choices=[(1, 'Student'), (2, 'Teacher'), (3, 'HOD')]),
        ),
    ]
