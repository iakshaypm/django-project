# Generated by Django 5.0.4 on 2024-04-21 12:10

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0003_alter_account_is_staff'),
    ]

    operations = [
        migrations.CreateModel(
            name='Subject',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subject', models.CharField(max_length=80)),
            ],
        ),
        migrations.AlterModelOptions(
            name='hod',
            options={},
        ),
        migrations.AlterModelOptions(
            name='teacher',
            options={},
        ),
        migrations.AlterField(
            model_name='teacher',
            name='subject',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='user.subject'),
        ),
    ]
