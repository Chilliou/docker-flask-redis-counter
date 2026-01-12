import time
import redis
import os
from flask import Flask, request
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from deep_translator import GoogleTranslator

app = Flask(__name__)

# --- CONFIG REDIS ---
redis_host = os.environ.get('REDIS_HOST', 'localhost')
try:
    cache = redis.Redis(host=redis_host, port=6379, socket_connect_timeout=1)
except Exception:
    cache = None

# --- MOTEUR IA ---
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


def analyze_sentiment(text_fr):
    try:
        # 1. TRADUCTION (FR -> EN)
        # VADER marche mieux en anglais, donc on traduit l'input utilisateur
        translator = GoogleTranslator(source='auto', target='en')
        text_en = translator.translate(text_fr)

        # 2. ANALYSE VADER
        scores = analyzer.polarity_scores(text_en)
        compound = scores['compound']

        # 3. INTERPRETATION
        if compound >= 0.05:
            return "POSITIF 😃", "#28a745", compound
        elif compound <= -0.05:
            return "NÉGATIF 😡", "#dc3545", compound
        else:
            return "NEUTRE 😐", "#ffc107", compound

    except Exception as e:
        return f"Erreur : {str(e)}", "black", 0


@app.route('/', methods=['GET', 'POST'])
def home():
    try:
        count = get_hit_count()
    except any:
        count = "Erreur"

    # Valeurs par défaut
    user_input = ""
    result_text = "En attente de votre texte..."
    result_color = "#6c757d"
    score = 0

    # SI L'UTILISATEUR A ENVOYÉ LE FORMULAIRE
    if request.method == 'POST':
        user_input = request.form.get('user_text', '')
        if user_input:
            result_text, result_color, score = analyze_sentiment(user_input)

    # PAGE HTML AVEC FORMULAIRE
    return f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>DevOps Project</title>
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, \
                sans-serif; background-color: #f4f4f9; text-align: center; \
                padding: 20px; }}
            .container {{ background: white; padding: 40px; border-radius:\
                  12px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); max-width:\
                      600px; margin: auto; }}
            h1 {{ color: #333; }}
            textarea {{ width: 100%; height: 100px; padding: 10px; margin-top:\
                  10px; border-radius: 5px; border: 1px solid #ccc;\
                    font-family: sans-serif; }}
            input[type="submit"] {{ background-color: #007bff; color: white;\
              border: none; padding: 10px 20px; font-size: 16px;\
                  border-radius: 5px; cursor: pointer; margin-top: 10px; }}
            input[type="submit"]:hover {{ background-color: #0056b3; }}
            .result-box {{ margin-top: 20px; padding: 20px;\
                  border-radius: 8px;\
                  background-color: #f8f9fa;\
                    border: 2px solid {result_color}; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚀 DevOps & IA Analyzer</h1>
            <p>Analysez vos émotions en Français \
                (Pipeline : Traduction -> VADER)</p>
            <form method="POST">
                <textarea name="user_text" placeholder="Écrivez votre phrase\
                      ici (ex: J'adore ce cours de DevOps !)...">{user_input}\
                        </textarea>
                <br>
                <input type="submit" value="Analyser le sentiment">
            </form>

            <div class="result-box">
                <h2 style="color: {result_color}; margin: 0;">{result_text}\
                    </h2>
                <p>Score IA : <strong>{score}</strong></p>
            </div>

            <br>
            <p style="color: #888;">Visites totales : {count}</p>
        </div>
    </body>
    </html>
    '''


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
