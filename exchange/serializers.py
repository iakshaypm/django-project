from django.contrib.auth import (get_user_model, authenticate, )
from .models import Question, Comment, Upvote
from rest_framework import serializers, exceptions


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ['title', 'description']

    def create(self, validated_data):
        validated_data['user'] = self.context.get('user')
        return Question.objects.create(**validated_data)


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['content', 'question']


class UpvoteSerializer(serializers.ModelSerializer):
    class Meta:
        modal = Upvote
        fields = ['comment']
