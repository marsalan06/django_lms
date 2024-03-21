from rest_framework import serializers
from .models import DescriptiveQuestion, DescriptiveAnswer


class DescriptiveQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = DescriptiveQuestion
        fields = "__all__"


class DescriptiveAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = DescriptiveAnswer
        fields = "__all__"
