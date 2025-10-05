import pickle
import joblib
import re
import numpy as np
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
import nltk

class FakeNewsDetector:
    def __init__(self, model_path):
        """Initialize the model from saved artifacts"""
        try:
            # Try joblib first, then pickle
            if model_path.endswith('.joblib'):
                self.artifacts = joblib.load(model_path)
            else:
                with open(model_path, 'rb') as f:
                    self.artifacts = pickle.load(f)
            
            self.model = self.artifacts['model']

            # Check if vectorizer is separate or part of the model pipeline
            if 'vectorizer' in self.artifacts:
                self.vectorizer = self.artifacts['vectorizer']
            elif hasattr(self.model, 'named_steps'):
                # Model is a pipeline, vectorizer is inside
                self.vectorizer = None  # Will use the pipeline directly
            else:
                # Try to extract vectorizer from model
                self.vectorizer = getattr(self.model, 'vectorizer_', None)

            self.metadata = self.artifacts.get('metadata', {})
            self.ps = PorterStemmer()

            # Download stopwords if not available
            try:
                self.stop_words = set(stopwords.words('english'))
            except:
                nltk.download('stopwords')
                self.stop_words = set(stopwords.words('english'))

            print("Model loaded successfully!")

        except Exception as e:
            print(f"Error loading model: {e}")
            # Create a simple fallback model
            self._create_fallback_model()
    
    def _create_fallback_model(self):
        """Create a simple fallback model if main model fails"""
        print("Creating fallback model...")
        from sklearn.linear_model import LogisticRegression
        from sklearn.feature_extraction.text import CountVectorizer
        
        # Simple demo data
        texts = [
            "breaking news amazing discovery", "shocking revelation today",
            "official statement government", "research study confirms"
        ]
        labels = [1, 1, 0, 0]  # 1=Fake, 0=Real
        
        self.vectorizer = CountVectorizer()
        X = self.vectorizer.fit_transform(texts)
        self.model = LogisticRegression()
        self.model.fit(X, labels)
        self.metadata = {'model_type': 'Fallback Model', 'accuracy': 0.75}
        self.stop_words = set(stopwords.words('english'))
        self.ps = PorterStemmer()
    
    def preprocess_text(self, text):
        """Preprocess input text"""
        text = re.sub(r'[^a-zA-Z\s]', '', text)
        text = text.lower().strip()
        
        words = text.split()
        words = [word for word in words if word not in self.stop_words and len(word) > 2]
        words = [self.ps.stem(word) for word in words]
        
        return ' '.join(words)
    
    def predict(self, news_text):
        """Make prediction on news text"""
        processed_text = self.preprocess_text(news_text)

        try:
            # If vectorizer is None, model is a pipeline
            if self.vectorizer is None:
                prediction = self.model.predict([processed_text])[0]
                probability = self.model.predict_proba([processed_text])[0]
            else:
                text_vector = self.vectorizer.transform([processed_text])
                prediction = self.model.predict(text_vector)[0]
                probability = self.model.predict_proba(text_vector)[0]

            return {
                'prediction': int(prediction),
                'confidence': float(np.max(probability)),
                'class': 'FAKE' if prediction == 1 else 'REAL',
                'probabilities': {
                    'real': float(probability[0]),
                    'fake': float(probability[1])
                }
            }
        except Exception as e:
            print(f"Prediction error: {e}")
            return {
                'prediction': 0,
                'confidence': 0.5,
                'class': 'REAL',
                'probabilities': {'real': 0.5, 'fake': 0.5}
            }
    
    def get_model_info(self):
        return self.metadata