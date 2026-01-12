import time
import redis
import os
import random
import boto3
from flask import Flask


app = Flask(__name__)

redis_host = os.environ.get('REDIS_HOST', 'localhost')
try:
    cache = redis.Redis(host=redis_host, port=6379, socket_connect_timeout=1)
except Exception:
    cache = None


try:
    translate = boto3.client('translate', region_name='eu-north-1')
    ai_available = True
except Exception:
    ai_available = False


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
        return base_text

    target_lang = random.choice(['en', 'es', 'de', 'ja', 'fr'])

    if target_lang == 'fr':
        return base_text

    try:
        result = translate.translate_text(
            Text=base_text,
            SourceLanguageCode='fr',
            TargetLanguageCode=target_lang
        )
        return f"{result['TranslatedText']} \
            (Traduit par AWS AI en {target_lang})"
    except Exception as e:
        print(f"Erreur AI: {e}")
        return base_text


@app.route('/')
def hello():
    try:
        count = get_hit_count()
        message = get_translated_message()
    except Exception:
        count = "Erreur"
        message = "Erreur"

    return f'''
    <div style="text-align: center; margin-top: 50px; font-family: sans-serif;">
        <h1>🚀 DevOps & AI Project</h1>
        <h2 style="color: #007bff;">{message}</h2>
        <br>
        <p>Visites : <strong>{count}</strong></p>
        <p><small>Powered by AWS ECS, Terraform & Amazon Translate (ML)</small></p>
    </div>
    '''


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
