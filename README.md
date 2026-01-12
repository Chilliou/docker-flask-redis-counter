# ☁️ Cloud Native DevOps Project : Flask, Redis & Embedded AI

![AWS](https://img.shields.io/badge/AWS-EU%20North%201-orange)
![Terraform](https://img.shields.io/badge/IaC-Terraform-purple)
![CI/CD](https://img.shields.io/badge/CI%2FCD-GitHub%20Actions-blue)
![Machine Learning](https://img.shields.io/badge/AI-Embedded%20NLP-green)

Projet de Master 2 (IWOCS) combinant **Infrastructure as Code**, **Intégration Continue** et **Machine Learning**.
L'application est une plateforme interactive d'analyse de sentiments, déployée sur une architecture AWS Serverless.

## 🏗 Architecture Technique

Le projet repose sur une architecture micro-services résiliente :

* **Frontend/Backend :** Python Flask.
* **Cache :** Redis (Pattern *Sidecar* pour une latence nulle).
* **Machine Learning :** Pipeline NLP hybride (Deep Translator + VADER) embarqué dans le conteneur.
* **Infrastructure AWS :**
    * **ECS Fargate :** Exécution Serverless des conteneurs.
    * **ALB (Application Load Balancer) :** Répartition de charge et point d'entrée unique.
    * **ECR (Elastic Container Registry) :** Stockage des images Docker.
    * **VPC Custom :** Réseau isolé avec sous-réseaux publics/privés.

## 🚀 Fonctionnalités Clés

### 1. Infrastructure as Code (IaC)
Toute l'infrastructure est décrite via **Terraform**.
* Déploiement reproductible en une commande (`terraform apply`).
* Gestion des rôles IAM (Sécurité), des Security Groups et du Réseau.

### 2. Pipeline CI/CD (DevOps)
Automatisation complète via **GitHub Actions** :
* Linter Python (Flake8) pour garantir la qualité du code (Quality Gate).
* Build de l'image Docker multi-stage.
* Push automatique vers AWS ECR.
* Déploiement continu sur ECS (Zero Downtime).

### 3. Intelligence Artificielle (Embedded ML)
Intégration d'un module d'analyse de sentiment (NLP) :
* Traduction automatique (Français -> Anglais).
* Analyse de polarité (Positif/Négatif/Neutre) via l'algorithme VADER.
* Exécution **Edge Computing** (dans le conteneur) pour réduire les coûts et la latence.

## 🛠️ Comment déployer (Localement)

### Pré-requis
* AWS CLI configuré (`aws configure`).
* Terraform installé.

### Installation
1.  Cloner le dépôt :
    ```bash
    git clone [https://github.com/ton-user/ton-repo.git](https://github.com/ton-user/ton-repo.git)
    cd terraform
    ```

2.  Lancer l'infrastructure :
    ```bash
    terraform init
    terraform apply
    ```

3.  Accéder à l'application :
    L'URL du Load Balancer s'affichera dans le terminal à la fin du déploiement (Output `app_url`).

## 📸 Aperçu

<img width="728" height="631" alt="image" src="https://github.com/user-attachments/assets/cd948281-6ce1-45de-80a2-6f79e5a9e20f" />

---
*Projet réalisé dans le cadre du Master 2 IWOCS - Université Le Havre Normandie*
