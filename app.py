import os
from flask import Flask, session, render_template, request, redirect, url_for, send_file
import joblib
import pandas as pd
import io
from fpdf import FPDF

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret")

# Charger le modèle
model = joblib.load("model/lgbm_clf.pkl")

# Liste des questions du chatbot dans l'ordre
questions = [
    ("annual_inc", "Quel est votre revenu annuel (€) ?", "Exprimé en brut annuel, sans centimes."),
    ("loan_amnt", "Quel est le montant du prêt souhaité (€) ?", "Montant total que vous souhaitez emprunter."),
    ("int_rate", "Quel est le taux d'intérêt proposé (%) ?", "Ex. : 7.5"),
    ("dti", "Quel est votre ratio dette/revenu (DTI %) ?", "Plus il est bas, mieux c’est. Ex. : 35%"),
    ("revol_util", "Quel est votre taux d'utilisation du crédit (%) ?", "Ex. : 50% d'utilisation des cartes"),
    ("credit_history_length", "Depuis combien d'années avez-vous un historique de crédit ?", "Ancienneté en années"),
    ("pub_rec", "Combien de défaillances publiques avez-vous ?", "Choisissez entre 0 et 3."),
    ("term", "Quelle est la durée du prêt ?", "En mois : 36 ou 60"),
    ("home_ownership", "Quel est votre statut de logement ?", "Ex. : Locataire, Propriétaire (hypothèque)"),
    ("purpose", "Quel est l'objet du prêt ?", "Ex. : Voiture, Travaux, Petite entreprise..."),
    ("verification", "Votre revenu est-il vérifié ?", "Oui ou Non"),
    ("installment", "Quel est le montant de la mensualité estimée (€) ?", "Ex. : 450")
]

question_options = {
    "term": ["36", "60"],
    "home_ownership": ["Locataire", "Propriétaire (hypothèque)", "Autre"],
    "purpose": ["Voiture", "Petite entreprise", "Travaux", "Autre"],
    "verification": ["Oui", "Non"],
    "pub_rec": ["0", "1", "2", "3"]
}

@app.route("/", methods=["GET", "POST"])
def chat():
    if 'step' not in session:
        session['step'] = 0
        session['answers'] = {}
        session['history'] = []

    step = session['step']
    answers = session['answers']
    history = session['history']
    result = None
    proba = None
    reco = None
    error = None
    download_ready = False

    if request.method == "POST":
        key, label, _ = questions[step]
        user_input = request.form['response'].strip()
        options = question_options.get(key)

        if options and user_input not in options:
            error = "Veuillez sélectionner une option valide."
            return render_template("chat.html", question=label, helper=questions[step][2], history=history, error=error, options=options)

        try:
            if not options:
                if key in ["annual_inc", "loan_amnt", "int_rate", "dti", "revol_util", "installment"]:
                    float(user_input)
                elif key == "credit_history_length":
                    int(user_input)
        except ValueError:
            error = "Entrée invalide. Merci de saisir une valeur numérique."
            return render_template("chat.html", question=label, helper=questions[step][2], history=history, error=error, options=None)

        answers[key] = user_input
        history.append((label, user_input))
        session['step'] = step + 1

        if session['step'] >= len(questions):
            input_data = {
                'int_rate': float(answers['int_rate']),
                'annual_inc': float(answers['annual_inc']),
                'revol_util': float(answers['revol_util']),
                'loan_amnt': float(answers['loan_amnt']),
                'dti': float(answers['dti']),
                'credit_history_length': int(answers['credit_history_length']),
                'installment': float(answers['installment']),
                'pub_rec': int(answers['pub_rec']),
                'term': 1 if answers['term'] == "60" else 0,
                'home_ownership_MORTGAGE': 1 if "hypoth" in answers['home_ownership'].lower() else 0,
                'purpose_small_business': 1 if "entreprise" in answers['purpose'].lower() else 0,
                'verification_status_Source Verified': 1 if answers['verification'].lower().startswith("oui") else 0
            }

            df = pd.DataFrame([input_data])
            prob = model.predict_proba(df)[0][1]
            proba = round(prob * 100, 1)

            if prob > 0.65:
                result = "🔴 Refusé"
                reco = "Votre profil présente actuellement un risque élevé."
            elif prob > 0.35:
                result = "🟡 Ajusté"
                reco = "Votre profil est acceptable, mais légèrement à risque. Des ajustements pourraient améliorer votre éligibilité."
            else:
                result = "🟢 Accepté"
                reco = "Félicitations ! Votre profil semble solide."

            session['result'] = result
            session['proba'] = proba
            session['reco'] = reco
            download_ready = True
            session['download_ready'] = True
            return render_template("chat.html", history=history, result=result, proba=proba, message=reco, download_ready=True)

    if session.get('step') is not None and session['step'] < len(questions):
        key, current_question, helper = questions[session['step']]
        options = question_options.get(key)
    else:
        current_question, helper, options = None, None, None

    return render_template("chat.html", question=current_question, helper=helper, options=options, history=history, result=result, proba=proba, message=reco, error=error, download_ready=download_ready)

@app.route("/download")
def download_pdf():
    if not session.get('download_ready'):
        return "PDF non disponible."

    def latin1_safe(text):
        return text.encode("latin-1", "ignore").decode("latin-1")

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Simulation de crédit - Résultat", ln=True, align='C')
    pdf.ln(10)

    for q, a in session['history']:
        q_clean = q.replace("€", "EUR")
        a_clean = a.replace("€", "EUR")
        pdf.multi_cell(0, 10, latin1_safe(f"{q_clean} : {a_clean}"))

    pdf.ln(5)
    pdf.cell(0, 10, latin1_safe(f"Probabilité de défaut : {session['proba']}%"), ln=True)
    pdf.cell(0, 10, latin1_safe(f"Décision : {session['result']}"), ln=True)
    reco_clean = session['reco'].replace('<br>', '\n')
    pdf.multi_cell(0, 10, latin1_safe(f"Recommandation : {reco_clean}"))

    # Génération propre du PDF en mémoire
    pdf_bytes = pdf.output(dest='S').encode('latin1')
    pdf_output = io.BytesIO(pdf_bytes)
    pdf_output.seek(0)

    return send_file(pdf_output, as_attachment=True, download_name="diagnostic_credit.pdf")

@app.route("/reset", methods=["GET"])
def reset():
    session.clear()
    return redirect(url_for("chat"))

if __name__ == "__main__":
    app.run() # debug=True
