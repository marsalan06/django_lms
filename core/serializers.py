from rest_framework import serializers
from .models import NewsAndEvents


class NewsAndEventsSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsAndEvents
        fields = "__all__"  # You can specify fields you want to include
