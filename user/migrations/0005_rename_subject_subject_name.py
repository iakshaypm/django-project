# Generated by Django 5.0.4 on 2024-04-21 13:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0004_subject_alter_hod_options_alter_teacher_options_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='subject',
            old_name='subject',
            new_name='name',
        ),
    ]
