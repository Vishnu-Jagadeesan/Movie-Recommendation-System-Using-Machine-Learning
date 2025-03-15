import pandas as pd
import nltk
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score
import pickle

# Download NLTK resources
nltk.download("stopwords")

def load_data():
    return pd.read_csv('datasets/reviews.txt', sep='\t', names=['sentiment', 'text'])

def create_model_pipeline():
    return Pipeline([
        ('tfidf', TfidfVectorizer(
            use_idf=True,
            lowercase=True,
            strip_accents='ascii',
            stop_words=stopwords.words('english'),  # Use list directly
            max_features=5000,
            ngram_range=(1, 2)
        )),
        ('clf', MultinomialNB(alpha=0.1))
    ])

def train_sentiment_model():
    # Load and split data
    df = load_data()
    X_train, X_test, y_train, y_test = train_test_split(
        df['text'], df['sentiment'], test_size=0.2, random_state=42
    )
    
    # Create and train pipeline
    model_pipeline = create_model_pipeline()
    model_pipeline.fit(X_train, y_train)
    
    # Evaluate
    train_acc = accuracy_score(y_train, model_pipeline.predict(X_train))
    test_acc = accuracy_score(y_test, model_pipeline.predict(X_test))
    print(f"Training Accuracy: {train_acc*100:.2f}%")
    print(f"Test Accuracy: {test_acc*100:.2f}%")
    
    # Save model
    with open('nlp_model.pkl', 'wb') as f:
        pickle.dump(model_pipeline, f)

if __name__ == '__main__':
    train_sentiment_model()