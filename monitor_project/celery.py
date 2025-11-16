import os
from celery import Celery

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'monitor_project.settings')

# Create the Celery application instance
app = Celery('monitor_project')

# Load task modules from all registered Django apps.
# This means Celery will look for a "tasks.py" file in each app.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks in all installed apps
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')