# Generated by Django 5.0.4 on 2024-05-08 06:50

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0008_alter_student_classroom'),
    ]

    operations = [
        migrations.AlterField(
            model_name='account',
            name='user_type',
            field=models.PositiveIntegerField(choices=[(1, 'Student'), (2, 'Teacher'), (3, 'HOD'), (4, 'Management'), (5, 'Parent')], default=1),
        ),
        migrations.CreateModel(
            name='Parent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('phone_number', models.CharField(max_length=20)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='student',
            name='parent',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='user.parent'),
            preserve_default=False,
        ),
    ]