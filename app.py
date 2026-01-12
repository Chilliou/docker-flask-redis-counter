import time
import redis
import os
import random
from flask import Flask
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer


app = Flask(__name__)
redis_host = os.environ.get('REDIS_HOST', 'localhost')
try:
    cache = redis.Redis(host=redis_host, port=6379, socket_connect_timeout=1)
except Exception:
    cache = None


analyzer = SentimentIntensityAnalyzer()


def get_hit_count():
    if cache is None:
        return "Indisponible (Mode sans Redis)"

    retries = 5
    while True:
        try:
            return cache.incr('hits')
        except redis.exceptions.ConnectionError:
            if retries == 0:
                return "Erreur Redis"
            retries -= 1
            time.sleep(0.5)


def get_ml_analysis():
    phrases = [
        "AWS ECS is absolutely amazing and fast!",
        "This error 503 is really annoying and bad.",
        "The deployment process with Terraform is smooth.",
        "I hate when the cloud bill is too high.",
        "DevOps makes life so much easier and happy."
    ]

    sentence = random.choice(phrases)

    scores = analyzer.polarity_scores(sentence)
    compound = scores['compound']

    if compound >= 0.05:
        emotion = "POSITIF 😃"
        color = "#28a745"
    elif compound <= -0.05:
        emotion = "NEGATIF 😡"
        color = "#dc3545"
    else:
        emotion = "NEUTRE 😐"
        color = "#ffc107"

    return sentence, emotion, color, round(compound, 2)


@app.route('/')
def hello():
    try:
        count = get_hit_count()
        text, sentiment, color, score = get_ml_analysis()
    except Exception as e:
        count = "Erreur"
        text = str(e)
        sentiment = "Erreur"
        color = "black"
        score = 0

    return f'''
    <div style="text-align: center; \
        margin-top: 50px; font-family: sans-serif;">
        <h1>🚀 DevOps & Embedded ML</h1>
        <p>Le conteneur analyse cette phrase en temps réel :</p>
        <h3 style="font-style: italic;">"{text}"</h3>
        <hr style="width: 50%; margin: 20px auto;">
        <p>Verdict du Modèle IA :</p>
        <h2 style="color: {color};">{sentiment} (Score: {score})</h2>
        <br>
        <p>Visites : <strong>{count}</strong></p>
        <p><small>Powered by ECS Fargate & VADER NLP (Local ML)</small></p>
    </div>
    '''


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
