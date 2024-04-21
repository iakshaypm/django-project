from django.contrib import admin
from .models import Question, Comment, Upvote
# Register your models here.
models = [Question, Comment, Upvote]
admin.site.register(models)

