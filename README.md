# 🐳 Docker Flask Redis Counter

![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Redis](https://img.shields.io/badge/redis-%23DD0031.svg?style=for-the-badge&logo=redis&logoColor=white)

> **Projet de démonstration d'une architecture micro-services conteneurisée.**
> Ce projet illustre l'orchestration entre un frontend (Flask) et une base de données (Redis) via Docker Compose, avec une gestion stricte des réseaux et des variables d'environnement.

---

## 🏗 Architecture

L'application est composée de deux services isolés :

1.  **Web App (Python/Flask)** : Sert l'interface utilisateur et communique avec la base de données.
2.  **Database (Redis Alpine)** : Stocke le nombre de visites (Stateful).

**Points techniques clés :**
* Isolation des processus via **Docker Containers**.
* Communication inter-conteneurs via un **Bridge Network** privé (DNS interne).
* Configuration dynamique via **Environment Variables** (Pas de hardcoding d'IPs).
* Optimisation de l'image Python (utilisation de l'image `slim` et gestion du cache des layers).

---

## 🚀 Démarrage Rapide

### Prérequis
* Docker & Docker Compose installés.

### Installation

1.  **Cloner le dépôt**
    ```bash
    git clone https://github.com/Chilliou/docker-flask-redis-counter.git
    cd docker-flask-redis-counter
    ```

2.  **Lancer la stack (Build & Run)**
    ```bash
    docker-compose up --build -d
    ```

3.  **Accéder à l'application**
    Ouvrir le navigateur à l'adresse : [http://localhost:8000](http://localhost:8000)

4.  **Arrêter les services**
    ```bash
    docker-compose down
    ```

---

## 📂 Structure du Projet

```bash
.
├── app.py              # Code source de l'application Flask
├── Dockerfile          # Instructions de build de l'image Web
├── docker-compose.yml  # Orchestration des services & Réseau
├── requirements.txt    # Dépendances Python
└── README.md           # Documentation
```

## 🛠 Commandes Utiles
Vérifier les logs du conteneur web :

```Bash

docker-compose logs -f web
```
Vérifier l'état des conteneurs :

```Bash

docker-compose ps
```
Accéder au shell du conteneur Redis :

```Bash
docker-compose exec redis_db sh
```

## 👤 Auteur
Chilliou - Ingénieur DevOps Junior
