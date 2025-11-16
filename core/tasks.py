import requests
import hashlib
import os
import joblib  # <-- NEW: To load our model
from bs4 import BeautifulSoup
from celery import shared_task
from django.conf import settings # <-- NEW: To get BASE_DIR
from .models import ScrapeTarget, Insight  # <-- NEW: Import Insight

# --- NEW: Load the AI Model on startup ---
# We load the model once when the worker starts, not inside the task
MODEL_PATH = os.path.join(settings.BASE_DIR, 'ml_model', 'text_classifier.joblib')
try:
    text_classifier = joblib.load(MODEL_PATH)
    print("--- AI text classifier model loaded successfully. ---")
except FileNotFoundError:
    print(f"--- FATAL: AI Model not found at {MODEL_PATH} ---")
    print("--- Please run 'python ml_model/train_model.py' ---")
    text_classifier = None # Set to None so app can still run

# -----------------------------------------------------------------------------
# MASTER SCHEDULER TASK (Unchanged)
# -----------------------------------------------------------------------------
@shared_task
def schedule_all_scrapes():
    """
    This is the "master task" run by Celery Beat.
    It finds all active scrape targets and creates a separate
    'scrape_url' task for each one.
    """
    print("--- Running Master Scrape Scheduler ---")
    active_targets = ScrapeTarget.objects.filter(is_active=True)
    count = 0
    for target in active_targets:
        scrape_url.delay(target.id)
        count += 1
    
    print(f"--- Queued {count} scrape tasks ---")
    return f"Queued {count} scrape tasks"


# -----------------------------------------------------------------------------
# INDIVIDUAL SCRAPER TASK (UPDATED)
# -----------------------------------------------------------------------------
@shared_task
def scrape_url(target_id):
    """
    The main scraping task.
    Fetches a URL, parses text, checks for changes, CLASSIFIES, and SAVES.
    """
    if text_classifier is None:
        print(f"[Scraper Task {target_id}]: AI Model is not loaded. Aborting task.")
        return "Error: AI Model not loaded."

    try:
        target = ScrapeTarget.objects.get(id=target_id, is_active=True)
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        print(f"[Scraper Task {target_id}]: Fetching {target.url}...")
        response = requests.get(target.url, headers=headers, timeout=10)
        response.raise_for_status() 

        soup = BeautifulSoup(response.text, 'html.parser')
        
        # --- NEW: Try to find a good title ---
        title = soup.title.string if soup.title else None
        if not title:
            h1 = soup.find('h1')
            if h1:
                title = h1.get_text(strip=True)
            else:
                h2 = soup.find('h2')
                if h2:
                    title = h2.get_text(strip=True)
        # Fallback title if none found
        if not title:
            title = f"Update from {target.competitor.name}"

        body_text = ' '.join(soup.body.get_text(separator=' ', strip=True).split())
        
        if not body_text:
            print(f"[Scraper Task {target_id}]: No text found for {target.url}. Skipping.")
            return

        current_hash = hashlib.md5(body_text.encode('utf-8')).hexdigest()

        if current_hash == target.last_scraped_hash:
            print(f"[Scraper Task {target_id}]: No changes detected for {target.url}")
            return

        # ======================================================================
        # --- CHANGE DETECTED! ---
        # ======================================================================
        print(f"[Scraper Task {target_id}]: CHANGE DETECTED for {target.url}")

        # 8. --- NEW: Classify the text ---
        predicted_category = text_classifier.predict([body_text])[0]
        print(f"[Scraper Task {target_id}]: Classified as: {predicted_category}")

        # 9. --- NEW: Create a new Insight record in the database ---
        Insight.objects.create(
            competitor=target.competitor,
            target=target,
            title=title.strip(),
            summary=body_text[:1000] + "...", # Store a 1000-char snippet
            category=predicted_category,
            source_url=target.url
            # event_date defaults to now(), which is perfect
        )
        print(f"[Scraper Task {target_id}]: New Insight SAVED to database.")

        # 10. Update the target's hash in the database
        target.last_scraped_hash = current_hash
        target.save()
        
        return f"Successfully scraped, classified, and saved Insight for {target.url}"

    except ScrapeTarget.DoesNotExist:
        print(f"[Scraper Task {target_id}]: ScrapeTarget not found or is inactive.")
    except requests.exceptions.RequestException as e:
        print(f"[Scraper Task {target_id}]: Error fetching {target.url}: {e}")
    except Exception as e:
        print(f"[Scraper Task {target_id}]: An unexpected error occurred: {e}")