from rest_framework import viewsets, permissions
from .models import Competitor, Insight
from .serializers import CompetitorSerializer, InsightSerializer

class CompetitorViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows competitors to be viewed or edited.
    """
    queryset = Competitor.objects.all().order_by('name')
    serializer_class = CompetitorSerializer

class InsightViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows insights to be viewed or edited.
    """
    queryset = Insight.objects.all().order_by('-event_date')
    serializer_class = InsightSerializer
    # permission_classes = [permissions.IsAuthenticated]