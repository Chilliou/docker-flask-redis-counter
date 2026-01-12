import time
import redis
import os
import random
import boto3
from flask import Flask


app = Flask(__name__)

# --- CONFIG REDIS ---
redis_host = os.environ.get('REDIS_HOST', 'localhost')
try:
    cache = redis.Redis(host=redis_host, port=6379, socket_connect_timeout=1)
except Exception:
    cache = None


ai_error_init = None
try:
    translate = boto3.client('translate', region_name='eu-north-1')
    ai_available = True
except Exception as e:
    ai_available = False
    ai_error_init = str(e)


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


def get_translated_message():
    base_text = "L'application est en ligne sur AWS ECS !"

    if not ai_available:
        return f"Erreur Init IA : {ai_error_init}"

    target_lang = random.choice(['en', 'es', 'de', 'ja', 'fr'])

    if target_lang == 'fr':
        return base_text + " (Français par hasard)"

    try:
        result = translate.translate_text(
            Text=base_text,
            SourceLanguageCode='fr',
            TargetLanguageCode=target_lang
        )
        return f"{result['TranslatedText']} (Traduit en {target_lang})"
    except Exception as e:
        # ICI : On retourne l'erreur technique pour que tu la voies
        return f"ERREUR APPEL AWS : {str(e)}"


@app.route('/')
def hello():
    try:
        count = get_hit_count()
        message = get_translated_message()
    except Exception as e:
        count = "Erreur"
        message = f"Gros Crash : {str(e)}"

    return f'''
    <div style="text-align: center; \
        margin-top: 50px; font-family: sans-serif;">
        <h1>🚀 DevOps & AI Project</h1>
        <h2 style="color: #007bff;">{message}</h2>
        <br>
        <p>Visites : <strong>{count}</strong></p>
        <p><small>Debug Mode Active</small></p>
    </div>
    '''


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
