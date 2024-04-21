from django.contrib.auth import (get_user_model, authenticate, )
from .models import Question, Comment, Upvote
from rest_framework import serializers, exceptions


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ['title', 'description', 'tag']


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['content', 'question']


class UpvoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Upvote
        fields = ['comment']

    def validate(self, attrs):
        comment = attrs['comment']
        exists = Upvote.objects.filter(comment=attrs['comment']).exists()
        if exists:
            raise serializers.ValidationError({'comment': 'You cannot upvote the same comment.'})
        return attrs
