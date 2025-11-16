from rest_framework import serializers
from .models import Competitor, Insight, ScrapeTarget

class CompetitorSerializer(serializers.ModelSerializer):
    """
    Serializes the Competitor model.
    """
    class Meta:
        model = Competitor
        fields = ['id', 'name', 'website_url', 'created_at']


class InsightSerializer(serializers.ModelSerializer):
    """
    Serializes the Insight model.
    We'll include the competitor's name for easy display.
    """
    # This uses the __str__ method of the Competitor model
    competitor_name = serializers.CharField(source='competitor.name', read_only=True)
    
    # This gets the "human-readable" version of the category choice
    category_display = serializers.CharField(source='get_category_display', read_only=True)

    class Meta:
        model = Insight
        fields = [
            'id', 
            'competitor', 
            'competitor_name', #custom field
            'title', 
            'summary', 
            'category',
            'category_display', #custom field
            'source_url', 
            'event_date'
        ]
        # 'competitor' is write-only, we show 'competitor_name' for reading.
        extra_kwargs = {
            'competitor': {'write_only': True}
        }