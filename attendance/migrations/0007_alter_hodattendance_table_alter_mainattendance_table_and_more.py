# Generated by Django 5.0.4 on 2024-04-21 12:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('attendance', '0006_alter_hodattendance_table_alter_mainattendance_table_and_more'),
    ]

    operations = [
        migrations.AlterModelTable(
            name='hodattendance',
            table='attendance_hod',
        ),
        migrations.AlterModelTable(
            name='mainattendance',
            table='attendance_main',
        ),
        migrations.AlterModelTable(
            name='studentattendance',
            table='attendance_student',
        ),
        migrations.AlterModelTable(
            name='teacherattendance',
            table='attendance_teacher',
        ),
    ]
