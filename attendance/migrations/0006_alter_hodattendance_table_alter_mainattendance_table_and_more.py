# Generated by Django 5.0.4 on 2024-04-21 12:29

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('attendance', '0005_alter_hodattendance_date_of_marking_and_more'),
    ]

    operations = [
        migrations.AlterModelTable(
            name='hodattendance',
            table='hod',
        ),
        migrations.AlterModelTable(
            name='mainattendance',
            table='main',
        ),
        migrations.AlterModelTable(
            name='studentattendance',
            table='student',
        ),
        migrations.AlterModelTable(
            name='teacherattendance',
            table='teacher',
        ),
    ]
