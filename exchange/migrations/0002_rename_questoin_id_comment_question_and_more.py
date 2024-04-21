# Generated by Django 5.0.4 on 2024-04-18 17:22

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('exchange', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RenameField(
            model_name='comment',
            old_name='questoin_id',
            new_name='question',
        ),
        migrations.RenameField(
            model_name='comment',
            old_name='user_id',
            new_name='user',
        ),
        migrations.RenameField(
            model_name='question',
            old_name='user_id',
            new_name='user',
        ),
        migrations.RenameField(
            model_name='upvote',
            old_name='comment_id',
            new_name='comment',
        ),
        migrations.RenameField(
            model_name='upvote',
            old_name='user_id',
            new_name='user',
        ),
        migrations.AddField(
            model_name='question',
            name='tag',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterUniqueTogether(
            name='upvote',
            unique_together={('comment', 'user')},
        ),
    ]
