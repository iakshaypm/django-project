from rest_framework import serializers

from .models import Assignment, AssignmentMark


class AssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assignment
        fields = ['name', 'type']


class AssignmentMarkSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssignmentMark
        fields = ['assignment', 'mark']
