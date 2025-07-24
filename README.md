# 📊 Crédit pour Tous – Simulation de Risque de Défaut de Paiement

Ce projet est une application web développée avec **Flask** permettant de prédire le risque de défaut d’un client à partir de ses informations financières. Elle s’inscrit dans un cas d’usage réel de la société fictive **« Crédit pour Tous »**, spécialisée dans le prêt peer-to-peer.

L’interface conversationnelle guide l’utilisateur à travers une série de questions pour estimer ses chances d’obtenir un prêt, tout en respectant les principes du RGPD et les bonnes pratiques d’UX/UI.

---

# 🎯 Objectif

Faciliter l'évaluation des demandes de prêt en automatisant l'analyse du risque grâce à un modèle de machine learning et une interface conversationnelle.

## 🧠 Fonctionnalités principales

- Dialogue étape par étape avec l'utilisateur
- Prédiction du risque de défaut à partir d'un modèle pré-entraîné (`lgbm_clf.pkl`)
- Interface utilisateur responsive et intuitive (HTML + CSS)
- Affichage de la probabilité de défaut et d’une évaluation du profil
- Génération d’un rapport PDF du diagnostic
- Simulation de scénarios “et si…”

---

## ⚙️ Technologies

- Python 3.x
- Flask
- Pandas, Joblib
- FPDF (pour génération PDF)
- HTML / CSS (templates Jinja2)

---

## 🛠️ Installation

1. **Clone ou télécharge ce dépôt**
   ```bash
   git clone https://github.com/christianKT/credit_pour_tous.git
---

## 📂 Structure du projet

```
credit_pour_tous/
│
├── app.py                          # Script principal Flask
├── requirements.txt               # Dépendances Python
├── Dockerfile                     # Image Docker pour le déploiement
├── README.md                      # Présentation du projet
├── .gitignore                     # Fichiers/dossiers à ignorer
│
├── model/
│   └── lgbm_clf.pkl               # Modèle LGBM pré-entraîné
│
├── templates/
│   └── chat.html                  # Interface HTML du chatbot
│
├── notebooks/                     # Notebooks d'analyse et modélisation
│   ├── 1_EDA.ipynb                # Analyse exploratoire
│   └── 2_model_training.ipynb     # Construction et évaluation du modèle
│
└── data/
    ├── raw/                       
    │   └── Classeur1.csv          # Données brutes (à ne pas versionner)
    │
    └── processed_data/
        └── features.csv           # Données traitées (features)

```

---

## 🚀 Déploiement

Cette app peut être facilement déployée sur **render** :

1. Fork ou clone ce repo
2. Assure-toi que `requirements.txt` est bien défini
3. Déploie sur 

---

## 👤 Auteur

Projet réalisé dans le cadre d’un travail IA / MLOps  
🔗 [CK | Crédit pour Tous]