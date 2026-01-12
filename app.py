import time
import redis
import os
from flask import Flask

app = Flask(__name__)

redis_host = os.environ.get('REDIS_HOST', 'localhost')
try:
    cache = redis.Redis(host=redis_host, port=6379, socket_connect_timeout=1)
except Exception as e:
    cache = None

def get_hit_count():
    if cache is None:
        return "Indisponible (Mode sans Redis)"
    
    retries = 5
    while True:
        try:
            return cache.incr('hits')
        except redis.exceptions.ConnectionError as exc:
            if retries == 0:
                return "Erreur Redis"
            retries -= 1
            time.sleep(0.5)

@app.route('/')
def hello():
    try:
        count = get_hit_count()
    except Exception:
        count = "Erreur connection"
        
    return f'''
    <div style="text-align: center; margin-top: 50px; font-family: sans-serif;">
        <h1>🚀 DevOps M2 IWOCS</h1>
        <p>L'application est en ligne sur AWS ECS !</p>
        <br>
        <p>Visites : <strong>{count}</strong></p>
        <p><small>Déployé via Terraform & GitHub Actions</small></p>
    </div>
    '''

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)