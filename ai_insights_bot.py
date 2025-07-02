from transformers import pipeline
from textblob import TextBlob
from sklearn.feature_extraction.text import CountVectorizer
import numpy as np

# Load Hugging Face pipelines
sentiment_analyzer = pipeline("sentiment-analysis")
summarizer = pipeline("summarization")


def analyze_sentiment(text):
    result = sentiment_analyzer(text)[0]
    return {
        "label": result['label'],
        "score": round(result['score'], 2)
    }


def summarize_text(text, max_length=60, min_length=30):
    summary = summarizer(text, max_length=max_length, min_length=min_length, do_sample=False)
    return summary[0]['summary_text']


def extract_keywords(text, top_n=5):
    vectorizer = CountVectorizer(stop_words='english')
    word_matrix = vectorizer.fit_transform([text])
    word_counts = word_matrix.toarray().sum(axis=0)
    word_freq = [(word, word_counts[idx]) for word, idx in vectorizer.vocabulary_.items()]
    sorted_words = sorted(word_freq, key=lambda x: x[1], reverse=True)
    return [word for word, freq in sorted_words[:top_n]]


if __name__ == '__main__':
    user_input = """
    OpenAI has released several powerful models in the last few years.
    Developers are now able to integrate language models into applications with ease.
    However, ethical AI development is still a concern for many organizations.
    """

    print(" Sentiment Analysis:", analyze_sentiment(user_input))
    print(" Summary:", summarize_text(user_input))
    print(" Keywords:", extract_keywords(user_input))
