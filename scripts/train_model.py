#!/usr/bin/env python3
"""
Script to train the sentiment analysis model for Smart Review Analyzer
"""

import pandas as pd
import pickle
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report
import nltk
from nltk.corpus import stopwords
import os

# Download required NLTK data
nltk.download('stopwords', quiet=True)
nltk.download('punkt', quiet=True)

def create_sample_data():
    """Create sample training data for demonstration."""
    sample_reviews = [
        # Positive reviews
        "This product is amazing! I love it so much.",
        "Excellent quality and fast shipping. Highly recommended!",
        "Great value for money. Very satisfied with my purchase.",
        "Outstanding customer service and product quality.",
        "Perfect! Exactly what I was looking for.",
        "Fantastic product, exceeded my expectations.",
        "Best purchase I've made in a while. Five stars!",
        "Love it! Will definitely buy again.",
        "Superb quality and design. Very happy.",
        "Incredible product, works perfectly.",
        
        # Negative reviews
        "Terrible product, complete waste of money.",
        "Poor quality, broke after one day of use.",
        "Worst purchase ever. Very disappointed.",
        "Cheap materials and bad construction.",
        "Don't buy this, it's garbage.",
        "Horrible experience, product doesn't work.",
        "Overpriced for such poor quality.",
        "Regret buying this. Money wasted.",
        "Disappointing product, not as described.",
        "Failed to meet expectations. Very poor.",
        
        # Neutral reviews
        "It's okay, nothing special but works.",
        "Average product, meets basic expectations.",
        "Decent quality for the price paid.",
        "Not bad, not great either. Just okay.",
        "Standard product, does what it says.",
        "Acceptable quality, could be better.",
        "Fair product, worth considering.",
        "Reasonable option, nothing outstanding.",
        "Good enough for basic needs.",
        "Satisfactory product overall."
    ]
    
    # 0 = negative, 1 = positive, 2 = neutral
    labels = [1] * 10 + [0] * 10 + [2] * 10
    
    return sample_reviews, labels

def preprocess_text(text):
    """Basic text preprocessing."""
    # Convert to lowercase
    text = text.lower()
    
    # Remove special characters and digits
    import re
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    
    # Remove extra whitespace
    text = ' '.join(text.split())
    
    return text

def train_model():
    """Train the sentiment analysis model."""
    print("Creating sample training data...")
    texts, labels = create_sample_data()
    
    # Preprocess texts
    processed_texts = [preprocess_text(text) for text in texts]
    
    print("Splitting data...")
    X_train, X_test, y_train, y_test = train_test_split(
        processed_texts, labels, test_size=0.2, random_state=42, stratify=labels
    )
    
    print("Creating TF-IDF vectorizer...")
    vectorizer = TfidfVectorizer(
        max_features=1000,
        stop_words='english',
        ngram_range=(1, 2)
    )
    
    X_train_tfidf = vectorizer.fit_transform(X_train)
    X_test_tfidf = vectorizer.transform(X_test)
    
    print("Training logistic regression model...")
    model = LogisticRegression(
        random_state=42,
        max_iter=1000,
        class_weight='balanced'
    )
    
    model.fit(X_train_tfidf, y_train)
    
    # Evaluate model
    y_pred = model.predict(X_test_tfidf)
    accuracy = accuracy_score(y_test, y_pred)
    
    print(f"Model accuracy: {accuracy:.3f}")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, target_names=['Negative', 'Positive', 'Neutral']))
    
    # Create models directory if it doesn't exist
    os.makedirs('models', exist_ok=True)
    
    # Save model and vectorizer
    print("Saving model...")
    with open('models/sentiment_model.pkl', 'wb') as f:
        pickle.dump(model, f)
    
    print("Saving vectorizer...")
    with open('models/vectorizer.pkl', 'wb') as f:
        pickle.dump(vectorizer, f)
    
    print("Model training completed successfully!")
    print("Files saved:")
    print("- models/sentiment_model.pkl")
    print("- models/vectorizer.pkl")

if __name__ == "__main__":
    train_model()
