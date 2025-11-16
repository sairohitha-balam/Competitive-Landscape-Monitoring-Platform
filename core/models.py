from django.db import models
from django.utils import timezone

# This is a base model to add "created_at" and "updated_at"
# fields to all our other models. It's good practice.
class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Competitor(TimeStampedModel):
    """Stores a single competitor we want to track."""
    name = models.CharField(max_length=255, unique=True)
    website_url = models.URLField(max_length=500, blank=True, null=True)
    
    # We can add more fields later (e.g., twitter_handle, linkedin_url)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


class ScrapeTarget(TimeStampedModel):
    """
    Stores a specific URL (or target) to be scraped for a competitor.
    e.g., A competitor's blog, pricing page, or 'news' section.
    """
    TARGET_CHOICES = [
        ('BLOG', 'Blog'),
        ('PRICING', 'Pricing Page'),
        ('NEWS', 'News/Announcements'),
        ('CAREERS', 'Careers Page'),
        ('OTHER', 'Other'),
    ]
    
    competitor = models.ForeignKey(Competitor, on_delete=models.CASCADE, related_name='targets')
    url = models.URLField(max_length=1000)
    target_type = models.CharField(max_length=10, choices=TARGET_CHOICES, default='OTHER')
    
    # We'll use this hash to detect if the page content has changed
    last_scraped_hash = models.CharField(max_length=64, blank=True, null=True)
    
    # We can use this to temporarily disable a scraper that is failing
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.competitor.name} - {self.get_target_type_display()}"

    class Meta:
        # Ensures we don't scrape the same URL for the same competitor twice
        unique_together = ('competitor', 'url')


class Insight(TimeStampedModel):
    """
    This is the "golden" record. A single piece of structured
    intelligence we found about a competitor.
    """
    CATEGORY_CHOICES = [
        ('RELEASE', 'Product Release'),
        ('CAMPAIGN', 'Marketing Campaign'),
        ('PRICING', 'Pricing Change'),
        ('HIRING', 'Key Hiring'),
        ('NEWS', 'News/PR'),
        ('UNKNOWN', 'Unknown'),
    ]

    competitor = models.ForeignKey(Competitor, on_delete=models.CASCADE, related_name='insights')
    target = models.ForeignKey(ScrapeTarget, on_delete=models.SET_NULL, null=True, blank=True, related_name='insights')
    
    title = models.CharField(max_length=500)
    summary = models.TextField(blank=True, null=True)
    category = models.CharField(max_length=10, choices=CATEGORY_CHOICES, default='UNKNOWN')
    
    source_url = models.URLField(max_length=1000)
    # The date the event *happened* (as best we can tell)
    event_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.competitor.name} - {self.get_category_display()}: {self.title}"

    class Meta:
        ordering = ['-event_date']