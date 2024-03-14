from rest_framework import generics
from .models import NewsAndEvents
from .serializers import NewsAndEventsSerializer

# from django.contrib.auth.decorators import login_required
from rest_framework.permissions import AllowAny


class NewsAndEventsList(generics.ListAPIView):
    serializer_class = NewsAndEventsSerializer
    permission_classes = [AllowAny]  # Ensure the user is logged in

    def get_queryset(self):
        """
        Restricts the returned news and events to the ones belonging to the given organization,
        by filtering against an organization_id in the URL.
        """
        # Retrieve the organization_id from URL parameters
        organization_id = self.kwargs.get("organization_id")
        queryset = NewsAndEvents.objects.filter(
            organization_id=organization_id
        ).order_by("-updated_date")
        return queryset
