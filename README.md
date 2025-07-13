# 📊 Crédit pour Tous – Simulation de Risque de Défaut de Paiement

Ce projet est une application web développée avec **Streamlit** permettant de prédire le risque de défaut d’un client à partir de ses informations financières. Elle s’inscrit dans un cas d’usage réel de la société fictive **« Crédit pour Tous »**, spécialisée dans le prêt peer-to-peer.

---

## 🎯 Objectif

Permettre à des analystes ou clients de :

- Simuler une demande de prêt
- Évaluer la **probabilité de défaut** en temps réel
- Obtenir une **explication visuelle** des résultats (optionnel)
- Sauvegarder les simulations en accord avec la RGPD

---

## 🧠 Intelligence Artificielle

Le modèle utilisé est un **VotingClassifier hybride pondéré** composé de :

- `RandomForestClassifier`
- `XGBoostClassifier`
- `LightGBMClassifier`

Les modèles ont été optimisés (hyperparamètres via `RandomizedSearchCV`) et entraînés sur des données réelles transformées :
- Scaling avec `MinMaxScaler`
- Encodage one-hot des variables catégorielles

---

## 🖥️ Interface

L’application propose **2 modes d’utilisation** :

- 📝 **Formulaire classique** avec tous les champs manuels
- 💬 **Assistant IA** simulant un chatbot pas à pas

Les simulations peuvent être enregistrées **anonymement** si l’utilisateur donne son consentement explicite ✅

---

## 📂 Structure du projet

```
credit_pour_tous/
│
├── app.py                     # Application principale Streamlit
├── requirements.txt           # Dépendances Python
├── README.md                  # Présentation du projet
│
├── model/
│   ├── voting_model.pkl       # Modèle hybride entraîné
│   └── scaler.pkl             # Scaler MinMax utilisé pour la normalisation
│
└── data/
    └── simulation_result/
        └── simulations_historique.csv  # Historique sauvegardé
```

---

## 🚀 Déploiement

Cette app peut être facilement déployée sur **Streamlit Cloud** :

1. Fork ou clone ce repo
2. Assure-toi que `requirements.txt` est bien défini
3. Déploie sur https://streamlit.io/cloud

---

## 📌 Dépendances principales

- `streamlit`
- `pandas`, `numpy`
- `scikit-learn`
- `xgboost`
- `lightgbm`
- `joblib`

---

## 👤 Auteur

Projet réalisé dans le cadre d’un travail IA / MLOps  
🔗 [Streamlit | Crédit pour Tous]