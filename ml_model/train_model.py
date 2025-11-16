import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
import joblib
import os

# Define file paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, 'training_data.csv')
MODEL_FILE = os.path.join(BASE_DIR, 'text_classifier.joblib')

def train_model():
    print(f"Loading training data from {DATA_FILE}...")
    # 1. Load Data
    try:
        df = pd.read_csv(DATA_FILE)
    except FileNotFoundError:
        print(f"Error: training_data.csv not found at {DATA_FILE}")
        return

    # Filter out any rows with missing data
    df = df.dropna(subset=['text', 'category'])
    
    X = df['text']
    y = df['category']
    
    if len(X) == 0:
        print("Error: No training data found. CSV might be empty or formatted incorrectly.")
        return

    print(f"Found {len(X)} training examples.")
    
    # 2. Create an ML Pipeline
    # A "pipeline" chains steps together.
    # TfidfVectorizer: Converts text into a matrix of numbers
    # MultinomialNB: A simple, fast, and effective classifier for text
    text_classifier = Pipeline([
        ('tfidf', TfidfVectorizer(stop_words='english')),
        ('clf', MultinomialNB()),
    ])

    print("Training the model...")
    # 3. Train the model
    text_classifier.fit(X, y)

    # 4. Save the trained model
    print(f"Saving model to {MODEL_FILE}...")
    joblib.dump(text_classifier, MODEL_FILE)
    
    print("\n--- Model Training Complete ---")
    print(f"Model saved to {MODEL_FILE}")
    
    # 5. Test the model with some examples
    print("\n--- Running quick test... ---")
    test_data = [
        "Our new pricing is now live, starting at $20",
        "We are excited to launch our new AI assistant",
        "Come join our team, we are hiring a new developer"
    ]
    
    predictions = text_classifier.predict(test_data)
    for text, category in zip(test_data, predictions):
        print(f"Text: '{text}'  =>  Predicted: '{category}'")

if __name__ == "__main__":
    train_model()