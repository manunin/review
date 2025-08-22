"""
Machine Learning service for sentiment analysis
"""

import pickle
import re
import string
from typing import Dict, List
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer

from app.core.config import settings


class MLService:
    """Service for machine learning operations."""
    
    def __init__(self):
        self.model = None
        self.vectorizer = None
        self.lemmatizer = WordNetLemmatizer()
        self._load_model()
        self._download_nltk_data()
    
    def _download_nltk_data(self):
        """Download required NLTK data."""
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt')
        
        try:
            nltk.data.find('corpora/stopwords')
        except LookupError:
            nltk.download('stopwords')
            
        try:
            nltk.data.find('corpora/wordnet')
        except LookupError:
            nltk.download('wordnet')
    
    def _load_model(self):
        """Load the trained model and vectorizer."""
        try:
            with open(settings.MODEL_PATH, 'rb') as f:
                self.model = pickle.load(f)
            
            with open(settings.VECTORIZER_PATH, 'rb') as f:
                self.vectorizer = pickle.load(f)
                
        except FileNotFoundError:
            # If models don't exist, create a simple demo model
            self._create_demo_model()
    
    def _create_demo_model(self):
        """Create a simple demo model for testing purposes."""
        # This is a placeholder - in production, you'd train on real data
        self.vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        self.model = LogisticRegression()
        
        # Demo training data
        demo_texts = [
            "This is great, I love it!",
            "Excellent product, highly recommend",
            "Amazing quality and fast shipping",
            "Terrible product, waste of money",
            "Poor quality, very disappointed",
            "Worst purchase ever, avoid this",
            "It's okay, nothing special",
            "Average product, meets expectations",
            "Neutral experience, not bad not good"
        ]
        demo_labels = [1, 1, 1, 0, 0, 0, 2, 2, 2]  # 0=negative, 1=positive, 2=neutral
        
        # Preprocess and train
        processed_texts = [self._preprocess_text(text) for text in demo_texts]
        X = self.vectorizer.fit_transform(processed_texts)
        self.model.fit(X, demo_labels)
    
    def _preprocess_text(self, text: str) -> str:
        """Preprocess text for analysis."""
        # Convert to lowercase
        text = text.lower()
        
        # Remove punctuation
        text = text.translate(str.maketrans('', '', string.punctuation))
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Tokenize
        tokens = word_tokenize(text)
        
        # Remove stopwords and lemmatize
        stop_words = set(stopwords.words('english'))
        tokens = [self.lemmatizer.lemmatize(token) for token in tokens if token not in stop_words]
        
        return ' '.join(tokens)
    
    def analyze_sentiment(self, text: str) -> Dict[str, any]:
        """
        Analyze sentiment of a text.
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary with sentiment and confidence
        """
        # Preprocess text
        processed_text = self._preprocess_text(text)
        
        # Vectorize
        text_vector = self.vectorizer.transform([processed_text])
        
        # Predict
        prediction = self.model.predict(text_vector)[0]
        probabilities = self.model.predict_proba(text_vector)[0]
        
        # Map prediction to sentiment
        sentiment_map = {0: "negative", 1: "positive", 2: "neutral"}
        sentiment = sentiment_map[prediction]
        
        # Get confidence (max probability)
        confidence = float(np.max(probabilities))
        
        return {
            "sentiment": sentiment,
            "confidence": confidence,
            "probabilities": {
                "negative": float(probabilities[0]),
                "positive": float(probabilities[1]) if len(probabilities) > 1 else 0.0,
                "neutral": float(probabilities[2]) if len(probabilities) > 2 else 0.0
            }
        }
    
    def analyze_batch(self, texts: List[str]) -> List[Dict[str, any]]:
        """
        Analyze sentiment for multiple texts.
        
        Args:
            texts: List of texts to analyze
            
        Returns:
            List of sentiment analysis results
        """
        results = []
        for text in texts:
            result = self.analyze_sentiment(text)
            results.append(result)
        
        return results
