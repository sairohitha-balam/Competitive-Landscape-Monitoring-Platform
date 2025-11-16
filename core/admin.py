from django.contrib import admin
from .models import Competitor, ScrapeTarget, Insight

@admin.register(Competitor)
class CompetitorAdmin(admin.ModelAdmin):
    list_display = ('name', 'website_url', 'created_at')
    search_fields = ('name',)

@admin.register(ScrapeTarget)
class ScrapeTargetAdmin(admin.ModelAdmin):
    list_display = ('competitor', 'target_type', 'url', 'is_active', 'updated_at')
    list_filter = ('competitor', 'target_type', 'is_active')
    search_fields = ('url', 'competitor__name')

@admin.register(Insight)
class InsightAdmin(admin.ModelAdmin):
    list_display = ('title', 'competitor', 'category', 'event_date')
    list_filter = ('category', 'competitor')
    search_fields = ('title', 'summary', 'competitor__name')
    date_hierarchy = 'event_date'